# Agent entrypoint — Filmworkbench Starter v0.1

Read `filmworkbench.json`, `docs/STACK.md` and `docs/QUICKSTART.md`. The machine-readable model manifest is `docs/model_sources.json`; it records exact filenames, quantization/precision, revisions, sizes, SHA-256 values and upstream sources. Node projects and pinned revisions are in `docs/DEPENDENCIES.md` and `docs/backend_source_snapshot.json`.

## Help the user get started

1. Identify the task: viewing examples, rerendering the first dialogue clip, preparing new references, or studying a full historical chain. Explain the supported scope before selecting requirements.
2. Inspect Python/FFmpeg availability and ask for or discover the user's local ComfyUI root/server. Run `python doctor.py` offline first, then `python doctor.py --online` against the local backend when available. It reports missing nodes/models and incompatible enumerated settings. Do not invent paths or infer GPU compatibility from model filenames.
3. Explain exactly what is missing and which original upstream source supplies it. `setup_models.py --comfy-root PATH` only plans; `--download` explicitly obtains the exact weights and verifies them; `--verify` reads installed files. Follow existing user authorization for installations/downloads; a read-only check alone is not permission to start them. Use the backend's own Python for ComfyUI dependencies, not an unrelated environment.
4. Use `--model-map file.json` for explicitly selected loader-relative paths. External model directories can be checked with `setup_models.py --model-root CATEGORY=PATH`. Never rename a different quantization to imitate the expected file. No low-memory alternative has been validated here.
5. When generation is requested and the backend is ready, run `python render_example.py --run --comfy-root PATH`. It performs S1, waits for success, feeds the new S1 latent into S2, then copies S1 audio into the final video. The five input pictures are supplied; no image API or Krea installation is necessary for this example.

## Working boundaries

Use one GPU job at a time; do not interrupt existing jobs. The runner refuses a busy queue and writes unique input/output paths. A timeout does not cancel its server job. Check the saved prompt ID before retrying. Preserve source files and keep credentials outside the repository.

The exact generator is Hybrid fl2va/ref2va b25–49 INT8. The required text encoder is not the chat agent. DMAD's filename contains `4step`, but the starter's S1 uses 8 sampling steps. Read the actual graph rather than inferring settings from labels.

The eight case exports plus marketplace are production evidence, not eight automatic replay programs. Read each `render-data/manifest.json`, the shared graph inventory and assembly record. Do not invent predecessor latents, skip unresolved dependencies or claim the full guided/autonomous director is installed. The public first-clip graph deliberately replaces historical `H3StageLatent` with stock AV joining.

For new image references, use the client's available GPT Image capability (`$imagegen` in supported Codex clients), an explicitly configured service/API, or the user's local Krea 2 setup. Do not assume another provider's skill works in this client. Do not start paid calls without authorization. Keep a coherent reference family and inspect the resulting spatial/state assumptions.

Successful rendering is not creative acceptance. Present the output and known limitations for review. Keep H3 outputs out of model training and include a visible MiniMax H3 credit when sharing. Third-party models/nodes retain their own terms; own code/docs are MIT. See `docs/CREDITS.md` and `docs/MEDIA.md`.
