"""Locked decode checks for Model B v3. No torch and no images."""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.decode import blend_probs, decode_one, decode_record, expected_grade

SPEC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "model_b_locked.json")


class DecodeTests(unittest.TestCase):
    def test_hierarchical_class_five_needs_p5_above_t5(self):
        probs = [0.05, 0.10, 0.20, 0.15, 0.05, 0.45]
        # p5 = 0.45 is the 6-way argmax, but it is not above t5 = 0.5 -> argmax of DR grades = 2.
        self.assertEqual(decode_one(probs, "hierarchical", 0.5), 2)
        self.assertEqual(decode_one(probs, "hierarchical", 0.40), 5)
        self.assertEqual(decode_one(probs, "argmax6"), 5)

    def test_hierarchical_boundary_is_strict(self):
        probs = [0.5, 0.0, 0.0, 0.0, 0.0, 0.5]
        self.assertEqual(decode_one(probs, "hierarchical", 0.5), 0)

    def test_ordinal_bins_are_inclusive_like_np_digitize(self):
        thr = [0.95, 1.45, 2.70, 3.15]
        # expected = 0.95 sits exactly on the first cut -> grade 1 (right=False).
        self.assertEqual(decode_one([0.05, 0.95, 0, 0, 0, 0], "hierarchical_ordinal", 0.475, thr), 1)
        self.assertEqual(decode_one([0.06, 0.94, 0, 0, 0, 0], "hierarchical_ordinal", 0.475, thr), 0)
        self.assertEqual(decode_one([0, 1, 0, 0, 0, 0], "hierarchical_ordinal", 0.475, thr), 1)
        self.assertEqual(decode_one([0, 0, 0, 0.8, 0.2, 0], "hierarchical_ordinal", 0.475, thr), 4)
        self.assertAlmostEqual(expected_grade([0, 0, 0, 0.8, 0.2, 0]), 3.2)

    def test_matches_numpy_digitize(self):
        try:
            import numpy as np
        except ImportError:
            self.skipTest("numpy not installed")
        rng = np.random.default_rng(0)
        thr = [0.60, 1.25, 2.35, 3.60]
        for _ in range(2000):
            p = rng.dirichlet(np.ones(6))
            part = p[:5] / p[:5].sum()
            ref = int(np.clip(np.digitize((part * np.arange(5)).sum(), thr), 0, 4))
            ref = 5 if p[5] > 0.675 else ref
            self.assertEqual(decode_one(p.tolist(), "hierarchical_ordinal", 0.675, thr), ref)
            ref_h = 5 if p[5] > 0.5 else int(np.argmax(p[:5]))
            self.assertEqual(decode_one(p.tolist(), "hierarchical", 0.5), ref_h)

    def test_argmax_tie_keeps_the_first_class(self):
        self.assertEqual(decode_one([0.2, 0.2, 0.2, 0.2, 0.2, 0.0], "hierarchical", 0.5), 0)

    def test_blend(self):
        out = blend_probs([[1, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 1]], [0.45, 0.40, 0.15])
        self.assertAlmostEqual(sum(out), 1.0)
        self.assertAlmostEqual(out[0], 0.45)
        self.assertAlmostEqual(out[5], 0.15)
        self.assertEqual(decode_one(out, "hierarchical", 0.5), 0)

    def test_locked_spec(self):
        with open(SPEC_PATH, "r", encoding="utf-8") as handle:
            spec = json.load(handle)
        ens = spec["ensemble"]
        self.assertEqual([b["key"] for b in spec["branches"]], ["vit3", "effb4", "e_twohead"])
        self.assertEqual([b["weight"] for b in spec["branches"]], [0.45, 0.40, 0.15])
        self.assertAlmostEqual(sum(ens["weights"].values()), 1.0)
        self.assertEqual(ens["decode"]["family"], "hierarchical")
        self.assertEqual(ens["decode"]["t5"], 0.5)
        self.assertEqual({b["img_size"] for b in spec["branches"]}, {384, 448})
        self.assertNotIn("resnet", json.dumps(spec["branches"]).lower())
        for branch in spec["branches"]:
            self.assertTrue(branch["checkpoint"].endswith(".pth"))
            decode_record([0.2, 0.2, 0.2, 0.2, 0.1, 0.1], branch["decode"])
        self.assertEqual(decode_record([0.1, 0.1, 0.1, 0.1, 0.1, 0.5], ens["decode"]), 0)


if __name__ == "__main__":
    unittest.main()
