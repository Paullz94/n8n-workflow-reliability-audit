import unittest

import prospect_ranker


class ProspectRankerTests(unittest.TestCase):
    def test_launch_gate_blocks_contact(self):
        doc = {
            "launch_enabled": False,
            "prospects": [{
                "id": "p1", "title": "A", "channel": "upwork",
                "contact_after_launch": True,
                "problem_fit": 3, "audit_first_fit": 3, "budget_signal": 3, "freshness": 3,
                "competition_penalty": 0, "proof_gap_penalty": 0,
            }],
        }
        rows = prospect_ranker.rank_queue(doc)
        self.assertFalse(rows[0]["contact_allowed_now"])
        self.assertEqual(prospect_ranker.rank_queue(doc, contactable_only=True), [])

    def test_research_only_remains_blocked_after_launch(self):
        doc = {
            "launch_enabled": True,
            "prospects": [{
                "id": "p1", "title": "Community", "channel": "make_community",
                "contact_after_launch": False,
                "problem_fit": 3, "audit_first_fit": 3, "budget_signal": 3, "freshness": 3,
                "competition_penalty": 0, "proof_gap_penalty": 0,
            }],
        }
        self.assertFalse(prospect_ranker.rank_queue(doc)[0]["contact_allowed_now"])

    def test_score_rewards_fit_and_penalizes_proof_gap(self):
        strong = {
            "problem_fit": 3, "audit_first_fit": 3, "budget_signal": 3, "freshness": 3,
            "competition_penalty": 0, "proof_gap_penalty": 0,
        }
        weak = dict(strong, proof_gap_penalty=2, competition_penalty=2)
        self.assertGreater(prospect_ranker.score(strong), prospect_ranker.score(weak))


if __name__ == "__main__":
    unittest.main()
