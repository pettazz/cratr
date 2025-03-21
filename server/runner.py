import logging

import boto3
import json

from config import Config
from fetcher import Fetcher

def lambda_handler(event, context):
  logging.getLogger().setLevel(logging.INFO)
  logger.debug(event)

  meteorites = Fetcher.fetch_classified_meteorites()

  secrets_manager = boto3.client("secretsmanager")
  secret_name = secrets_manager.get_secret_value(SecretId=Config().mysql.secret-arn)
  secret = json.loads(secret_name["SecretString"])
  db_user = secret["username"]
  db_pass = secret["password"]
  db_host = Config().mysql.host

  with mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_pass,
    database=Config().mysql.db_name
  ) as db:
    with db.cursor() as cursor:
      ids_query = "SELECT id FROM %s WHERE 1" % Config().mysql.table_name

      cursor.execute(ids_query)
      existing_ids = cursor.fetchall()
      new_ids = set([m["id"] for m in meteorites]) - set(existing_ids)
      new_meteorites = [m for m in meteorites if m["id"] not in new_ids]
      logger.info("found %d new meteorites with ids %s" % (len(new_meteorites), new_ids))

      in_query = "INSERT INTO %s (id, name, class, mass, year, lat, lon)" % Config().mysql.table_name + \
                 "VALUES (%(id)s, %(name)s, %(class)s, %(mass)s, %(year)s, %(lat)s, %(lon)s)"
      cursor.executemany(in_query, new_meteorites)
      cursor.commit()
      logger.debug("inserted %d new rows" % cursor.rowcount)

if __name__ == '__main__':
  # for running directly, locally
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        # logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
  )
  print(Fetcher.fetch_classified_meteorites())