# Two-pass dialogue starter

Use Python 3.11 or later. Set up the three public [node projects](DEPENDENCIES.md) and the six exact [model files](MODELS.md). For an existing backend, run the doctor first to see what is missing. No Python packages beyond the standard library are needed by this small runner. FFmpeg is required for final audio assembly. The original test hardware was an RTX 5090; this is not an automatic installer or a low-VRAM preset.

1. Run `python setup_models.py --comfy-root "C:/path/to/ComfyUI" --verify` to verify your weights. Then run `python render_example.py`. This reads the bundled first-dialogue-clip graphs and verifies each reference still's SHA-256 and node links.
2. Start your existing ComfyUI instance normally. Run `python render_example.py --check`. This reads `/object_info`; it does not submit a job or load a model for inference.
3. When the GPU is available and you want a render, run:

```console
python render_example.py --run --comfy-root "C:/path/to/ComfyUI"
```

The root must contain the `input` and `output` directories of the same locally running server. The default server is `http://127.0.0.1:8188`. The runner copies its stills under a unique `input/filmworkbench_v01/<run>/` path, renders S1, waits for successful completion, renders S2 from the saved S1 latent, then copies S1 audio under S2 video. It does not overwrite source files or run two generations concurrently.

`runs/<run>/` contains submitted graphs, server history, a source/output hash record and `dialogue_S2_S1audio.mp4`. The backend also retains its original clips and latents. Add the visible MiniMax H3 credit before sharing a newly generated clip; the eight distributed examples already carry it.

The default wait limit is one hour per stage. A timeout does **not** cancel the server job. Check the queue and saved prompt ID before restarting; do not submit a duplicate blindly.

This starter renders the first K1 dialogue clip only. It demonstrates reference preparation and the S1→latent-upscale→S2 path. It is not a replay of all eight edited films or the full chat director. To study another case, read its recipe, assembly JSON, API graphs and image bindings. Chained stages require the predecessor latents recorded in the graph; runtime latents are intentionally not shipped.

For models in category subdirectories, use the explicit `--model-map` option described in [model setup](MODELS.md). Windows and Linux use the same starter commands; adapt only your local paths and backend installation.
