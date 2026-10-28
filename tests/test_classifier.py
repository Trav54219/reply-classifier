import unittest

from reply_classifier.evaluate import evaluate, reply_rates
from reply_classifier.rules import classify


class RuleTests(unittest.TestCase):
    def test_machine_replies(self):
        self.assertEqual(classify("I am out of the office until Monday")[0], "out_of_office")
        self.assertEqual(classify("Dana no longer works at Acme")[0], "left_company")

    def test_unsubscribe_beats_everything_it_overlaps(self):
        self.assertEqual(classify("Please remove me from your list")[0], "unsubscribe")

    def test_negation_beats_interest(self):
        self.assertEqual(classify("Not interested, thanks")[0], "not_interested")
        self.assertEqual(classify("I'm interested, can we talk Thursday?")[0], "positive")

    def test_unknown_text_is_other(self):
        self.assertEqual(classify("")[0], "other")
        self.assertEqual(classify("Hmm")[0], "other")


class EvalTests(unittest.TestCase):
    def test_accuracy_and_per_label(self):
        rows = [{"text": "Unsubscribe", "label": "unsubscribe"},
                {"text": "Not interested", "label": "positive"}]
        res = evaluate(rows)
        self.assertEqual(res["accuracy"], 0.5)
        self.assertEqual(len(res["errors"]), 1)
        self.assertEqual(res["per_label"]["unsubscribe"]["precision"], 1.0)

    def test_denominator_is_contacted_not_replies(self):
        labels = ["out_of_office"] * 8
        r = reply_rates(576, labels)
        self.assertEqual(r["human_replies"], 0)
        self.assertEqual(r["human_reply_rate"], 0.0)
        self.assertAlmostEqual(r["raw_reply_rate"], 8 / 576)

    def test_positive_rate_over_contacted(self):
        r = reply_rates(100, ["positive", "positive", "not_interested", "out_of_office"])
        self.assertEqual(r["positive_rate"], 0.02)
        self.assertEqual(r["human_replies"], 3)


if __name__ == "__main__":
    unittest.main()
