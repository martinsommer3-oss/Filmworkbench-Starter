import shutil
import subprocess
import tempfile
import unittest
from array import array
from fractions import Fraction
from pathlib import Path

import film
from refinements import AUDIO_RATE, bridge_ambience, compensate_cut_marks, finish_ambience


class CutTimingTests(unittest.TestCase):
    def setUp(self):
        self.graph = film.load(film.ROOT / "graphs/MARKET_G2_S1.api.json")

    def test_shift_continuation_with_context_and_room(self):
        prompt = ("[Shot 1] Continue the motion.\n[Shot 2] At 00:03.300, cut.\n"
                  "[Shot 3] At 00:05.000, cut.\n[Shot 4] At 00:14.250, cut.")
        self.assertEqual(compensate_cut_marks(prompt, self.graph), prompt.replace("05.000", "05.333"))

    def test_opening_and_crowded_timing_stay_in_place(self):
        prompt = "[Shot 2] At 00:14.000, cut.\n[Shot 3] At 00:14.250, cut."
        opening = film.load(film.ROOT / "graphs/MARKET_G1_S1.api.json")
        self.assertEqual(compensate_cut_marks(prompt, self.graph), prompt)
        self.assertEqual(compensate_cut_marks("[Shot 2] At 00:05.000, cut.", opening),
                         "[Shot 2] At 00:05.000, cut.")

    def test_compiler_and_approval_fingerprint(self):
        with tempfile.TemporaryDirectory() as root:
            project = Path(root) / "film"
            plan = film.init(project, ["MARKET"])
            scene = plan["scenes"][0]
            name = "MARKET_G2_S1"
            state = {"jobs": {"01_MARKET/MARKET_G1_S1": {
                "status": "accepted", "latents": {"lat_s1": "previous.safetensors"},
            }}}
            original = film.fingerprint(project, scene, name)
            scene["compensate_continuation_cuts"] = True
            graph, _ = film.compile_graph(project, plan, scene, name, state, "test")
            self.assertIn("At 00:06.833", graph["40"]["inputs"]["prompt"])
            self.assertNotEqual(film.fingerprint(project, scene, name), original)
            self.assertIn("At 00:06.500", (project / scene["prompts"][name]).read_text(encoding="utf-8"))


class AmbienceTests(unittest.TestCase):
    def setUp(self):
        self.seam = AUDIO_RATE * 2
        self.samples = array("f", [0.01]) * (self.seam * 2) + array("f", [0.02]) * (self.seam * 2)

    def event(self, offset):
        start = (self.seam + round(offset * AUDIO_RATE)) * 2
        width = round(0.06 * AUDIO_RATE) * 2
        self.samples[start:start + width] = array("f", [0.6]) * width

    def test_transient_shortens_bridge_and_survives(self):
        self.event(0.8)
        source = self.samples[:]
        report = bridge_ambience(self.samples, self.seam, self.seam, self.seam)
        self.assertAlmostEqual(report["event_s"], 0.8)
        self.assertAlmostEqual(report["bridge_s"], 0.7)
        self.assertEqual(self.samples[:self.seam * 2], source[:self.seam * 2])
        self.assertAlmostEqual(self.samples[self.seam * 2], 0.01)
        untouched = (self.seam + round(0.7 * AUDIO_RATE)) * 2
        self.assertEqual(self.samples[untouched:], source[untouched:])

    def test_early_event_skips_bridge(self):
        self.event(0.3)
        source = self.samples[:]
        report = bridge_ambience(self.samples, self.seam, self.seam, self.seam)
        self.assertEqual(report["reason"], "event too close after seam")
        self.assertEqual(self.samples, source)

    def test_only_actual_incoming_motion_continuations(self):
        market = {"assembly": film.spec("MARKET"), "ambience_bridge_parts": ["MARKET_G3"]}
        self.assertEqual(film.bridge_selection(market), {2: "MARKET_G3"})
        cases = [("MARKET", "MARKET_G1"), ("K3", "K3_RETURN"), ("K4", "K4_INT_AUDIO")]
        for case, part in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                film.bridge_selection({"assembly": film.spec(case), "ambience_bridge_parts": [part]})

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg tools required")
    def test_ffmpeg_bridge_keeps_picture_and_duration(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.mp4"
            target = Path(directory) / "target.mp4"
            subprocess.run([
                "ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=blue:s=64x64:r=24:d=4",
                "-f", "lavfi", "-i", "sine=frequency=100:sample_rate=48000:duration=4",
                "-c:v", "libx264", "-c:a", "aac", str(source),
            ], check=True)
            output, report = finish_ambience(source, target, [Fraction(2), Fraction(2)], {1: "follow"})
            self.assertEqual(output, target)
            self.assertAlmostEqual(report["follow"]["bridge_s"], 1.5)
            for path in (source, target):
                self.assertEqual(film.probe(path)["streams"][0]["nb_frames"], "96")
            def video_hash(path):
                return subprocess.check_output([
                    "ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v", "-c", "copy", "-f", "hash", "-",
                ])
            self.assertEqual(video_hash(source), video_hash(target))


if __name__ == "__main__":
    unittest.main()
