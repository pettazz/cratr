import json, unittest

from classifier import Classifier

class TestClassifier(unittest.TestCase):

  def test_bad_classifiers(self):
    with self.assertRaises(ValueError) as ctx:
      c = Classifier("test/data/multiple_classifiers.json")
    self.assertTrue("duplicate classifier" in str(ctx.exception))

    # not actually a problem
    c2 = Classifier("test/data/missing_classifiers.json")
    self.assertIsInstance(c2, Classifier)

  def test_skippable_rocks(self):
    c = Classifier()
    with open("test/data/meteorites_missing_keys.json") as fin:
      meteorites = json.load(fin)
    classed = c.classify(meteorites)

    self.assertEqual(len(classed), 0)

  def test_empty_rocks(self):
    c = Classifier()
    classed = c.classify([])

    self.assertEqual(len(classed), 0)

  def test_blanked_classes(self):
    c = Classifier()
    with open("test/data/meteorites_blankable.json") as fin:
      meteorites = json.load(fin)
    classed = c.classify(meteorites)
    
    self.assertEqual(len(classed), 2)
    for m in classed:
      self.assertEqual(m["class"], "UNK")

  def test_unmatchable(self):
    c = Classifier()
    meteorites = [{
      "name": "Thumb Butte",
      "id": "53890",
      "nametype": "Valid",
      "recclass": "Q(rock)~1",
      "mass": "105",
      "fall": "Found",
      "year": "2008-01-01T00:00:00.000",
      "reclat": "35.169930",
      "reclong": "-114.455850",
    }]
    with self.assertRaises(ValueError) as ctx:
      classed = c.classify(meteorites)
    self.assertTrue("unmatched classification" in str(ctx.exception))
    
  def test_good_rocks(self):
    c = Classifier()
    with open("test/data/meteorites_good.json") as fin:
      meteorites = json.load(fin)
    classed = c.classify(meteorites)

    self.assertEqual(len(classed), 4)

    expected_classes = ["I", "IO", "LL", "LL"]
    found_classes = []
    for m in classed:
      found_classes.append(m["class"])
    self.assertTrue(all([ci in found_classes for ci in expected_classes]))