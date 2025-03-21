import unittest

from http import HTTPStatus
import httpx

from fetcher import Fetcher

class TestFetcher(unittest.TestCase):

  def test_404(self):
    test_client = httpx.Client(transport=httpx.MockTransport(
      lambda request: httpx.Response(
        HTTPStatus.NOT_FOUND,
        content="it does not here"
      )
    ))
    with self.assertRaises(httpx.HTTPStatusError) as ctx:
      Fetcher.fetch_classified_meteorites(httpx_client=test_client)

  def test_bad_rowcount_formats(self):
    test_client = httpx.Client(transport=httpx.MockTransport(
      lambda request: httpx.Response(
        HTTPStatus.OK,
        content='["lol"]'
      )
    ))
    with self.assertRaises(RuntimeError) as ctx:
      Fetcher.fetch_classified_meteorites(httpx_client=test_client)

    test_client = httpx.Client(transport=httpx.MockTransport(
      lambda request: httpx.Response(
        HTTPStatus.OK,
        content='[{"howmanyrowsyouwant": "several"}]'
      )
    ))
    with self.assertRaises(RuntimeError) as ctx:
      Fetcher.fetch_classified_meteorites(httpx_client=test_client)

  def test_empty(self):
    test_client = httpx.Client(transport=httpx.MockTransport(
      lambda request: httpx.Response(
        HTTPStatus.OK,
        content='[{"rowcount": 0}]'
      )
    ))
    res = Fetcher.fetch_classified_meteorites(httpx_client=test_client)
    self.assertEqual(len(res), 0)

  def test_good_rocks(self):
    with open("test/data/meteorites_good.json") as fin:
      good_data = fin.read()
    test_client = httpx.Client(transport=httpx.MockTransport(
      lambda request: httpx.Response(
        HTTPStatus.OK,
        content='[{"rowcount": 100}]'
      ) if b"rowcount" in request.url.query else httpx.Response(
        HTTPStatus.OK,
        content=good_data
      )
    ))
    res = Fetcher.fetch_classified_meteorites(httpx_client=test_client)
    self.assertEqual(len(res), 4)

