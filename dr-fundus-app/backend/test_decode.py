"""Locked decode checks. No torch and no images."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.decode import advanced_predict_one, blend_probs

THRESHOLDS = [0.95, 1.35, 2.35, 3.15]


class DecodeTests(unittest.TestCase):
    def test_class_five_wins_over_severity(self):
        probs = [0.2, 0.2, 0.2, 0.05, 0.05, 0.30]
        self.assertEqual(advanced_predict_one(probs, THRESHOLDS), 5)

    def test_expected_severity_bins(self):
        # Renormalized mass on class 0 only -> expected 0.
        self.assertEqual(advanced_predict_one([0.9, 0.02, 0.02, 0.02, 0.02, 0.02], THRESHOLDS), 0)
        # All mass on class 2 -> expected 2, which sits in [1.35, 2.35).
        self.assertEqual(advanced_predict_one([0, 0, 1, 0, 0, 0], THRESHOLDS), 2)
        # Boundary is inclusive, matching np.digitize(..., right=False).
        self.assertEqual(advanced_predict_one([0.05, 0.95, 0, 0, 0, 0], THRESHOLDS), 1)
        # Expected 3.2 is at or above 3.15.
        self.assertEqual(advanced_predict_one([0, 0, 0, 0.8, 0.2, 0], THRESHOLDS), 4)

    def test_argmax_tie_keeps_the_first_class(self):
        self.assertEqual(advanced_predict_one([0.2, 0.2, 0.2, 0.2, 0.2, 0.0], THRESHOLDS), 2)

    def test_locked_ensemble_weights(self):
        blended = blend_probs([1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1], 0.25, 0.75)
        self.assertAlmostEqual(blended[0], 0.25)
        self.assertAlmostEqual(blended[5], 0.75)
        self.assertEqual(advanced_predict_one(blended, THRESHOLDS), 5)


if __name__ == "__main__":
    unittest.main()
