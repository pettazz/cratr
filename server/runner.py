import logging

import boto3
import json
import mysql.connector

from config import Config
from fetcher import Fetcher

def lamdba_response(status, body):
  return {
    "isBase64Encoded": False,
    "statusCode": status,
    "body": json.dumps(body)
  }     

def lambda_handler(event, context):
  logging.getLogger().setLevel(logging.DEBUG)
  logger = logging.getLogger()
  logger.debug(event)

  secrets_manager = boto3.client("secretsmanager")
  secret_name = secrets_manager.get_secret_value(SecretId=Config().mysql.secret_arn)
  secret = json.loads(secret_name["SecretString"])
  db_user = secret["username"]
  db_pass = secret["password"]
  db_host = Config().mysql.host

  if "action" in event.keys():
    if event["action"] == "init-db":
      with mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database=Config().mysql.db_name
      ) as db:
        with db.cursor() as cursor:
          with open("create-table.sql") as fin:
            create_query = fin.read()
          cursor.execute(create_query)
          db.commit()

          show_query = "DESCRIBE %s.%s" % (Config().mysql.db_name, Config().mysql.table_name)
          result = cursor.execute(show_query)
          logger.debug(result)
          if Config().mysql.table_name in result:
            logger.info("table successfully created")
          else:
            raise RuntimeError("unable to create table!")
    elif event["action"] == "fetch":
      meteorites = Fetcher.fetch_classified_meteorites()

      with mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database=Config().mysql.db_name
      ) as db:
        with db.cursor(buffered=True) as cursor:
          ids_query = "SELECT id FROM %s WHERE 1" % Config().mysql.table_name
          cursor.execute(ids_query)
          existing_ids = [i[0] for i in cursor.fetchall()]
          logger.debug("found %s existing meteorites" % len(existing_ids))

          # likely remove this after testing
          if "force-refresh" in event.keys() and event["force-refresh"] == True:
            logger.debug("force refresh, truncating table")
            empty_q = "TRUNCATE TABLE %s" % Config().mysql.table_name
            cursor.execute(empty_q)
            db.commit()

            new_meteorites = meteorites
            logger.info("doing full refresh of %s meteorites" % len(meteorites))
          else:
            new_ids = set([m["id"] for m in meteorites]) - set(existing_ids)
            new_meteorites = [m for m in meteorites if m["id"] in new_ids]
            logger.info("found %s new meteorites with ids %s" % (len(new_meteorites), new_ids))

          if len(new_meteorites) > 0:
            ins_query = "INSERT INTO %s (id, name, class, mass, year, lat, lon)" % Config().mysql.table_name + \
                       "VALUES (%(id)s, %(name)s, %(class)s, %(mass)s, %(year)s, %(lat)s, %(lon)s)"
            cursor.executemany(ins_query, new_meteorites)
            db.commit()
            logger.debug("inserted %s new rows" % cursor.rowcount)
    else:
      logger.info("unrecognized action `%s` requested" % event["action"])

  elif "queryStringParameters" in event.keys():
    logger.debug("handling an API gateway request")

    required_fields = ["lat", "lon"]
    qs =event["queryStringParameters"]
    if not all([f in qs.keys() for f in required_fields]):
      logger.error("missing some required fields: %s" % required_fields)
      return lamdba_response(400, "missing some required fields: %s" % required_fields)
    else:
      req_lat = qs["lat"]
      req_lon = qs["lon"]
      radius_mi = qs["radius"] if "radius" in qs.keys() else Config().default_search_radius

      with mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database=Config().mysql.db_name
      ) as db:
        with db.cursor(buffered=True, dictionary=True) as cursor:
          local_query = """SELECT id, name, class, mass, year, lat, lon,
            (ST_Distance_Sphere(
              point(lon, lat),
              point(%s, %s)
            ) *.000621371192) AS distance
          FROM %s
            HAVING distance < %s
          ORDER BY distance
          """ % (req_lon, req_lat, Config().mysql.table_name, radius_mi)

          cursor.execute(local_query)
          found_meteorites = cursor.fetchall()
          logger.debug("found %s meteorites within %smi of (%s, %s)" % (
            len(found_meteorites),
            radius_mi,
            req_lat,
            req_lon
          ))
          logger.debug(found_meteorites)

          return lamdba_response(200, found_meteorites)

  else:
    logger.info("no action requested!")
    return lamdba_response(400, "no action requested")

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