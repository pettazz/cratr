import json, re
import httpx
from thefuzz import fuzz
from thefuzz import process

per_req_limit = 5000
base_url = "https://data.nasa.gov/resource/gh4g-9sfh.json"
rows_params = {"$query": "SELECT count(*) AS rowcount"}
limit_params = {"$limit": "%d" % per_req_limit, "$offset": "%(offset)d"}

headers = {
  "Content-Type": "application/json",
  "Accept": "application/json",
  "Accept-Encoding": "gzip, deflate, br"
}

try:
  response = httpx.get(base_url, params=rows_params, headers=headers)
  response.raise_for_status()
except httpx.RequestError as exc:
    raise Exception(f"An error occurred while requesting {exc.request.url!r}.")
except httpx.HTTPStatusError as exc:
    raise Exception(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")

total_rows = int(response.json()[0]["rowcount"])

meteorites = []

for i in range(0, total_rows, per_req_limit):
  req_params = {k: v % {"offset": i} for k, v in limit_params.items()}
  
  try:
    response = httpx.get(base_url, params=req_params, headers=headers)
    response.raise_for_status()
  except httpx.RequestError as exc:
      raise Exception(f"An error occurred while requesting {exc.request.url!r}.")
  except httpx.HTTPStatusError as exc:
      raise Exception(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")

  meteorites += response.json()

if len(meteorites) > 0:
  with open("known-classifications.json") as fin:
    classifications = json.load(fin)
    choices = []
    choice_map = {}
    for classification in classifications:
      choices += classification["classifiers"]

      for choice in classification["classifiers"]:
        if choice not in choice_map.keys():
          choice_map[choice] = classification["id"]
        else:
          raise Exception("duplicate classifier: " + choice)
  
  for meteorite in meteorites:
    clss = meteorite["recclass"]
    test = re.sub(r"\-|\(|\)|IMPACT|IMP|MELT|BRECCIA|ROCK|METAL|IRON,", " ", clss.upper())
    if not test.strip():
      print(clss, "blanked to", "?")
      cid = "?"
    else:
      matched = process.extractOne(test, choices, scorer=fuzz.token_sort_ratio)
      if not matched:
        raise Exception("unmatched classification: `%s` as `%s`" % (clss, test))

      cid = choice_map[matched[0]]
      print(clss, "->", cid)

