"""Checks for diagnostic errors that can silently invalidate robot experiments."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from read_state import Freshness
from inspect_episode import inspect


class FreshnessTests(unittest.TestCase):
    def test_duplicate_ticks_do_not_reset_progress(self):
        state = Freshness(0)
        self.assertEqual(state.status(.1, 1), "WAITING")
        state.update(4, .1)
        state.update(4, 1.2)
        self.assertEqual(state.status(1.3, 1), "FROZEN_TICK")
        state.update(0, 1.4)  # reset/wrap is still progress
        self.assertEqual(state.status(1.5, 1), "OK")
        self.assertEqual(state.status(2.5, 1), "NO_MESSAGES")


class EpisodeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "data.json"
        (self.path.parent / "image.ppm").write_bytes(b"P6\n1 1\n255\n\0\0\0")
        self.frame = {"idx": 0, "colors": {"color_0": "image.ppm"},
                      "states": {"left_arm": {"qpos": [0., .5]}},
                      "actions": {"left_arm": {"qpos": [.1, .6]}}}

    def run_inspect(self, frames):
        self.path.write_text(json.dumps({"data": frames}))
        return inspect(self.path, ["left_arm"])

    def test_valid_and_timing_limit(self):
        report, headers, rows = self.run_inspect([self.frame])
        self.assertEqual(report["frames"], 1)
        self.assertIn("NOT_VERIFIED", report["timing"])
        self.assertEqual(len(headers), len(rows[0]))

    def test_nonfinite(self):
        self.frame["actions"]["left_arm"]["qpos"][0] = float("nan")
        with self.assertRaises(ValueError):
            self.run_inspect([self.frame])

    def test_missing_and_outside_images(self):
        for image in ("missing.png", "../image.ppm"):
            self.frame["colors"]["color_0"] = image
            with self.assertRaises(ValueError):
                self.run_inspect([self.frame])

    def test_frame_gap(self):
        second = copy.deepcopy(self.frame)
        second["idx"] = 2
        with self.assertRaises(ValueError):
            self.run_inspect([self.frame, second])

    def test_dimension_change(self):
        second = copy.deepcopy(self.frame)
        second["idx"] = 1
        second["states"]["left_arm"]["qpos"].append(0)
        with self.assertRaises(ValueError):
            self.run_inspect([self.frame, second])


if __name__ == "__main__":
    unittest.main()
