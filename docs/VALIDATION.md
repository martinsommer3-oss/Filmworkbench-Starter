# Validation status — 7 November 2026

## v0.1.1: executable recipes and the three gates

All eight recipes plus MARKET completed their S1 chains from an extracted release package: **23 S1 stages**. K1, K2, K3 and K4 also completed full S2 chains and frame-exact film assembly; the first K6 S2 stage completed too (**11 S2 stages**). At the user's request, remaining S2 repetitions were omitted after these successful shared-path tests. They remain executable in the package, but are not claimed as freshly GPU-tested here.

| Case | S1 stages passed | S2 stages passed | Checked assembly | S1 / S2 wall seconds |
| --- | --- | --- | --- | --- |
| K1 | 2/2 | 2/2 | S2, 685 frames | 178.4 / 437.5 |
| K2 | 2/2 | 2/2 | S2, 685 frames | 184.9 / 609.3 |
| K3 | 3/3 | 3/3 | S2, 712 frames | 154.7 / 358.6 |
| K4 | 3/3 | 3/3 | S2, 729 frames | 163.4 / 365.2 |
| K6 | 3/3 | 1/3 | S1, 729 frames | 148.2 / 138.4 |
| K7 | 2/2 | 0/2 | S1, 685 frames | 177.9 / 0.0 |
| K8 | 2/2 | 0/2 | S1, 685 frames | 175.2 / 0.0 |
| K9 | 2/2 | 0/2 | S1, 685 frames | 181.1 / 0.0 |
| MARKET | 4/4 | 0/4 | S1, 1144 frames | 403.7 / 0.0 |

All 34 submitted render graphs exactly match the final packaged compiler. Each rendered video passed a complete video/audio decode. Each recipe's assembled S1 or S2 output passed its expected frame count and full decode; K4 includes the external dialogue prelap. The S1-only assemblies are technical preview checks, not new S2 examples. The gallery retains its previously selected S2 example videos.

All **43 CPU tests** passed from a fresh ZIP extraction in a directory containing spaces and an umlaut. They cover all 46 planned stage executions/dependencies, changed references and prompts, approval gates, timeouts/recovery state, retries and budgets, exact assembly frames/audio, and autonomous assessment integrity. `doctor.py --all --online` checked all 44 distinct case graphs after public-node adaptation: no missing node/model names or incompatible checked settings on the existing backend. Historical source graphs remain unchanged. [Recipe evidence](recipe_validation_v011.json) · [Packaged CPU evidence](package_cpu_validation_v011.json).

### Autonomous agent workflow check

The active agent inspected the newly rendered K1 test takes, recorded observations and end states, accepted four stages using the package's autonomous assessment commands, and assembled a **685-frame / 28.54-second S2 film** with S1 audio. This reused the technical test renders; it was **not** a fresh autonomous planning-to-render run. The shared render path was tested separately above.

The review used every 1 fps sample, exact seam/end frames and an existing local CPU Whisper/frame-analysis tool. That supplementary speech tool is not bundled. The intended dialogue is present in the transcript, with a possible added word. Cut timing differs from the prompts and the continuation ends slowly. Sampled frames and transcripts do not establish complete perceptual motion, voice quality or lip sync; these limitations are recorded rather than treated as a perfect result. [Agent review evidence](autonomous_validation_v011.json).

Gate 1's original first-clip S1/S2 runner has the separate baseline test below; image generation requires the user's configured image provider. Gate 2's dependencies, approval controls and complete recipe execution were tested. Gate 3's assessment/acceptance and assembly path was exercised by the active agent as described above; it is not a bundled independent director model. See [the three gates](GATES.md).

### What this does not establish

The existing Windows backend, RTX 5090 (32 GB VRAM) and 128 GB system RAM were used. This is not a clean foreign-machine GPU installation, lower-memory test, deterministic reproduction guarantee or controlled speed benchmark. Wall times include loading/polling and some CPU work ran concurrently. Model downloads, source revisions and hashes are documented separately; no model weights or upstream node code are bundled. A local or cloud agent still needs tools that can operate files/commands and inspect the media required by the task.

## Historical v0.1.0 baseline

- 20 CPU tests passed: real reference hashes, path confinement, missing nodes, renamed model paths, unsupported settings, busy queue, failed-render handling, model download/hash failures, overwrite refusal and public-node starter requirements.
- All 44 API graphs parse, their internal node links resolve and their image/audio loader inputs have packaged assets.
- Every recorded latent loader has a producer in the included graph inventory. This does not constitute a new GPU replay of those dependencies.
- All 35 input assets match their export SHA-256 values. The 31 public PNG inputs have no personal text metadata; embedded prompt metadata was removed from the Fantasy start-image copy without changing its pixels.
- Live read-only check of all 44 graphs against the existing workstation backend: no missing nodes, model filenames or checked required/enumerated settings. This archival schema check does not itself render or validate all chains.
- The eight S2 example videos were checked against their assembly hashes and decoded frame counts. Marketplace's English S2 export matches its validation hash. These are selected existing renders, not new replication results.
- Six speaking scene examples now have 23 English subtitle cues burned in; their decoded frame counts and audio packet payloads/timestamps match the original edits. Every cue and closing credit was visually inspected on QA stills. The two cases without German dialogue retain their original videos. Fantasy and marketplace also include English subtitles. A complete new listening review was not performed.
- Public text/JSON scanned for personal workstation identifiers, user directory paths and common credential patterns: no findings. This is a targeted check, not a claim that arbitrary data can safely be published.

## Remaining release limits

The source URLs, immutable revisions, target directories and hashes for all seven video-stack checkpoints are now documented. The six starter files total 52.6 GB. The helper verifies installed/downloaded bytes and preserves differing existing files. All seven local checkpoints were fully hashed and match; DMAD was verified in an external model directory.

A real fresh-machine **backend installation** is still untested: NVIDIA driver, CUDA/PyTorch wheels, ComfyUI dependency installation and lower-memory hardware may expose problems. Bulk internet download was not possible from the build environment (outbound Python networking was blocked); public source pages and published hashes were checked, and downloader failure paths were tested. Existing local files are not proof of a fresh download.

These baseline checks apply to v0.1.0, which only automated the first dialogue clip and did not include autonomous direction. v0.1.1 adds full recipes and bounded agent-directed operation as documented above. Image-generation installation remains separate.

## Complete starter run from the release package

The source ZIP was freshly extracted into a new directory containing a space and an umlaut. Its runner was launched from outside that directory with a new Python virtual environment, no pip and no inherited site-packages. The package uses its own five input images and unique new output prefixes. It successfully generated S1, loaded that newly saved latent for S2, and assembled the output with S1 audio.

- S1: **72.53 seconds**; S2: **184.03 seconds** wall time including polling.
- Output: **345 decoded frames, 14.375 seconds, 1952×1088, 24 fps**, H.264 video and stereo AAC audio.
- Full video/audio decode passed. Final video packet payloads/timestamps equal S2; final audio packet payloads/timestamps equal S1.
- Six visual spot-check frames inspected; this is a technical reproduction test, not a complete listening review or new creative acceptance.
- Hardware: RTX 5090, 32 GB VRAM, 128 GB system RAM. The existing backend was used; this is not a cold-start benchmark. Model hashing ran concurrently for part of the test.

The starter now depends on public ComfyUI, H3 Motion Context and LBH latent-upscale nodes only. Its S2 node 22 uses `LTXVConcatAVLatent` instead of the local timeline helper. [Machine-readable evidence](starter_validation.json) records runtime file hashes, tested ZIP hash, timings and output hash. Later documentation/gallery packaging changes do not alter those tested runner/graph files.

## Example gallery

All eight scene cases plus marketplace have newly rendered input/workflow overviews; Fantasy keeps its existing making-of. All nine new images were visually inspected, with automated image-loading and overflow checks. Each example opens with its video and overview, then links down to archived graph/settings copies and full-resolution references. Copy hashes and local Markdown/image links are checked during packaging. Videos retain their previously validated bytes; only their package paths changed.
