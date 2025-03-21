import logging

import httpx

from classifier import Classifier
from config import Config

class Fetcher:

  per_req_limit = 5000
  rows_params = {"$query": "SELECT count(*) AS rowcount"}
  limit_params = {"$limit": "%d" % per_req_limit, "$offset": "%(offset)d"}
  headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br"
  }

  @classmethod
  def _do_get(cls, params, client):
    logger = logging.getLogger(cls.__name__)

    try:
      response = client.get(Config().fetcher.uri, params=params)
      response.raise_for_status()
    except (httpx.HTTPStatusError, httpx.RequestError) as ex:
      logger.exception(ex)
      raise ex
    return response.json()

  @classmethod
  def fetch_classified_meteorites(cls, httpx_client=None):
    logger = logging.getLogger(cls.__name__)

    if httpx_client is None:
      httpx_client = httpx.Client(headers=cls.headers)

    with httpx_client as client:
      rows_response = cls._do_get(cls.rows_params, client)
      res_data = rows_response
      logger.debug(res_data)
      if not res_data[0] or "rowcount" not in res_data[0]:
        raise RuntimeError("unexpected response for row count query")
      total_rows = int(res_data[0]["rowcount"])
      logger.info("total rows: %d" % total_rows)

      meteorites = []
      for i in range(0, total_rows, cls.per_req_limit):
        req_params = {k: v % {"offset": i} for k, v in cls.limit_params.items()}
        logger.debug("requesting rows %d - %d" % (i, i + cls.per_req_limit))
        response = cls._do_get(req_params, client)
        meteorites += response

    logger.debug("fetched %s meteorites, classifying" % len(meteorites))
    c = Classifier()
    return c.classify(meteorites)