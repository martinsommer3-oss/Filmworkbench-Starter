"""Opt-in timing and finishing tools for the public recipe runner."""

from array import array
from fractions import Fraction
import math
import re
from statistics import median
import subprocess
import sys


FPS = 24
CUT_LEAD_FRAMES = 8
CUT_MARK = re.compile(r"(?im)^(\[Shot (?:[2-9]|[1-9]\d+)\][ \t]+At[ \t]+)(\d{2}):(\d{2}\.\d{3})(?=,)")
AUDIO_RATE = 48_000
CHANNELS = 2
WINDOW = AUDIO_RATE // 50


def continuation_geometry(graph):
    """Return the frame geometry only for a direct Motion Context continuation."""
    nodes = [node for node in graph.values() if node["class_type"] == "MiniMaxH3MotionContext"]
    if len(nodes) != 1:
        return None
    inputs = nodes[0]["inputs"]
    reference = graph[inputs["latent"][0]]["inputs"]
    return int(reference["length"]), int(inputs["context_length"])


def compensate_cut_marks(prompt, graph):
    geometry = continuation_geometry(graph)
    if geometry not in {(226, 56), (345, 56)}:
        return prompt
    raw_frames, context_frames = geometry
    marks = list(CUT_MARK.finditer(prompt))
    frames = [round((60 * int(match[2]) + float(match[3])) * FPS) for match in marks]
    adjusted = [
        frame + CUT_LEAD_FRAMES
        if frame >= context_frames + 2 * FPS and frame + CUT_LEAD_FRAMES < raw_frames
        else frame
        for frame in frames
    ]
    # Leave crowded or out-of-order prompts intact instead of reordering the cuts.
    if any(previous >= following for previous, following in zip(adjusted, adjusted[1:])):
        return prompt
    result = prompt
    for match, old_frame, new_frame in reversed(list(zip(marks, frames, adjusted))):
        if old_frame != new_frame:
            minutes, seconds = divmod(new_frame / FPS, 60)
            result = result[:match.start(2)] + f"{int(minutes):02d}:{seconds:06.3f}" + result[match.end(3):]
    return result


def frame_duration(stream):
    return Fraction(int(stream["nb_frames"])) / Fraction(stream["avg_frame_rate"])


def window_levels(samples, start, end):
    width = WINDOW * CHANNELS
    return [
        sum(value * value for value in samples[offset:offset + width]) / width
        for offset in range(start * CHANNELS, (end - WINDOW) * CHANNELS + 1, width)
    ]


def loud_windows(levels):
    threshold = max(median(levels) * 10 ** 0.6, 1e-12)
    return [value > threshold for value in levels]


def bridge_ambience(samples, seam, before, after):
    """Blend stereo float samples after a verified speech-free continuation seam."""
    limit = round(1.5 * AUDIO_RATE)
    before = min(before, seam, limit)
    after = min(after, len(samples) // CHANNELS - seam, limit)
    if min(before, after) < AUDIO_RATE // 2:
        return {"reason": "insufficient audio beside the seam"}

    before -= before % WINDOW
    loud_before = loud_windows(window_levels(samples, seam - before, seam))
    if any(loud_before[-5:]):
        return {"reason": "loud event reaches the seam"}
    quiet_before = before
    if any(loud_before):
        last_loud = max(index for index, loud in enumerate(loud_before) if loud)
        quiet_before -= (last_loud + 1) * WINDOW + round(0.14 * AUDIO_RATE)
    duration = min(quiet_before, after)
    if duration < AUDIO_RATE // 2:
        return {"reason": "insufficient quiet audio to mirror"}

    loud_after = loud_windows(window_levels(samples, seam, seam + after))
    event = next((index * WINDOW for index, (a, b) in enumerate(zip(loud_after, loud_after[1:])) if a and b), None)
    if event is not None and event - AUDIO_RATE // 10 < duration:
        duration = event - AUDIO_RATE // 10
        if duration < round(0.4 * AUDIO_RATE):
            return {"reason": "event too close after seam", "event_s": event / AUDIO_RATE}

    for frame in range(duration):
        angle = frame * math.pi / (2 * (duration - 1))
        outgoing = (seam - 1 - frame) * CHANNELS
        incoming = (seam + frame) * CHANNELS
        for channel in range(CHANNELS):
            value = samples[outgoing + channel] * math.cos(angle) + samples[incoming + channel] * math.sin(angle)
            samples[incoming + channel] = max(-1.0, min(1.0, value))
    return {"bridge_s": duration / AUDIO_RATE, "event_s": None if event is None else event / AUDIO_RATE}


def finish_ambience(source, target, durations, selected):
    """Use exact assembled part lengths and retain the existing video stream."""
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-nostdin", "-i", str(source), "-map", "0:a:0",
        "-ar", str(AUDIO_RATE), "-ac", str(CHANNELS), "-f", "f32le", "-",
    ])
    samples = array("f")
    samples.frombytes(raw)
    if sys.byteorder != "little":
        samples.byteswap()
    records = {}
    for index, name in selected.items():
        seam = round(sum(durations[:index]) * AUDIO_RATE)
        records[name] = {
            "seam_s": seam / AUDIO_RATE,
            **bridge_ambience(samples, seam, round(durations[index - 1] * AUDIO_RATE), round(durations[index] * AUDIO_RATE)),
        }
    if any("bridge_s" in record for record in records.values()):
        if sys.byteorder != "little":
            samples.byteswap()
        subprocess.run([
            "ffmpeg", "-v", "error", "-nostdin", "-n", "-i", str(source), "-f", "f32le",
            "-ar", str(AUDIO_RATE), "-ac", str(CHANNELS), "-i", "pipe:0",
            "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
            str(target),
        ], input=samples.tobytes(), check=True)
        return target, records
    return source, records
