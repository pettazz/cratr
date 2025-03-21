import logging
import json, re

from thefuzz import fuzz
from thefuzz import process

from config import Config

class Classifier:

  def __init__(self, classifier_defs_file=None):
    self.logger = logging.getLogger(self.__class__.__name__)
    if classifier_defs_file is None:
      classifier_defs_file = Config().classifier.default_defs
    self.logger.debug("using classifier definitions: %s" % classifier_defs_file)

    self.choices = []
    self.choice_map = {}

    with open(classifier_defs_file) as fin:
      classifications = json.load(fin)
      for classification in classifications:
        self.choices += classification["classifiers"]

        for choice in classification["classifiers"]:
          if choice not in self.choice_map.keys():
            self.choice_map[choice] = classification["id"]
          else:
            raise ValueError("duplicate classifier in definitions: " + choice)
    self.logger.info("loaded %d classifications" % len(self.choice_map))

  def classify(self, meteorites):
    classed_meteorites = []
       
    for meteorite in meteorites:
      required_keys = ["id", "name", "nametype", "recclass", "reclat", "reclong"]
      if not (set(required_keys).issubset(set(meteorite.keys())) and meteorite["nametype"] == "Valid"):
        self.logger.info("discarding row with invalid/missing data: %s" % meteorite)
      else:
        clss = meteorite["recclass"]
        test = re.sub(r"\-|\(|\)|IMPACT|IMP|MELT|BRECCIA|ROCK|METAL|IRON,", " ", clss.upper())
        if not test.strip():
          self.logger.debug("recclass `%s` reduced to empty, calling it unknown")
          cid = "UNK"
        else:
          matched = process.extractOne(test, self.choices, scorer=fuzz.token_sort_ratio)
          if not matched or matched[1] < Config().classifier.min_fuzz_score:
            raise ValueError("unmatched classification: `%s` as `%s`" % (clss, test))
          cid = self.choice_map[matched[0]]

        classed_meteorites.append({
          "id": int(meteorite["id"]),
          "name": meteorite["name"],
          "class": cid,
          "mass": float(meteorite["mass"] if "mass" in meteorite.keys() else 0),
          # these are str timestamps that are all jan 1 00:00:00
          "year": int(meteorite["year"][:4] if "year" in meteorite.keys() else 0), 
          "lat": float(meteorite["reclat"]),
          "lon": float(meteorite["reclong"])
        })

    return classed_meteorites