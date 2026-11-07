# What can be reproduced from this package?

## Included evidence

Eight selected scene recipes plus the marketplace case; 44 real API graphs; 31 PNG reference inputs and four synthetic WAV samples (two marketplace voices and two K4 dialogue/prelap inputs). Each graph preserves its prompts, seeds, sampling, conditioning, model filenames and node connections. The companion bindings files map image/audio loaders to included files. SHA-256 hashes identify the exported assets. The marketplace also has eight compact render records with original graph and predecessor hashes.

The [graph inventory](../graphs/inventory.json) maps every loaded AV latent to a producer included in this package. Generate those predecessors before dependent graphs. S1 and S2 parents must not be interchanged. film.py uses this dependency map to render all nine recipe plans; see VALIDATION.md for the actual tests.

## Try a self-contained example first

Run `python doctor.py` for offline file checks, then `python doctor.py --online` against your local ComfyUI. Use `--all` to include every case with the same public stage-join adapter used by film.py; unchanged historical graphs are retained on disk. The doctor reports missing nodes, model filenames, relative-path mismatches and incompatible enumerated settings. It never installs or downloads anything. It does not assume the presence of an image service merely because a chat client is installed.

The dialogue starter contains all of its input images, so neither GPT Image nor Krea 2 is needed to rerender that example. For new reference sets, GPT Image is recommended; Krea 2 is the local fallback. Matching opposite views and multi-view world sets still need review. A model substitution is a new variant requiring review, not identical reproduction.

Follow [guided filmmaking](GUIDED_FILM.md) for complete chains, own inputs and chat approvals. film.py handles predecessor renders, new output namespaces and assembly/audio decisions. The old [Quickstart](QUICKSTART.md) remains a minimal first-clip option. The K4 prelap is an extra audio-production step. Both synthetic source WAVs are included; the assembly JSON records the prelap placement. Recreating the original Qwen voice-generation process itself is outside this package.

## Portability and privacy

Private workstation paths become placeholders or relative asset paths. The public selection excludes chat logs, credentials, account settings, personal license documents and raw backend history. Image metadata is inspected; original picture pixels are preserved. Model weights and third-party node source are not bundled. Install dependencies from their upstream projects under their own terms.

File hashes establish which source was shared. GPU kernels, node changes and model variants can change regenerated results even with identical seeds. This candidate has not yet been proven on a clean foreign machine. It must not be advertised as a one-click complete Filmworkbench installation.
