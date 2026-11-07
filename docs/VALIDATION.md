# Validation status — 7 November 2026

Validation evidence for the v0.1.0 starter release.

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

Historical full-chain replay is not automated. Those graphs retain their original nodes, including `H3StageLatent`, whose locally installed timeline version was not available in the public main inspected. Only the runnable dialogue graph has been adapted to stock AV joining. The full guided/autonomous director and new-image generation integration are not packaged. GPT Image/Krea 2 are unnecessary for rerendering the included starter.

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
