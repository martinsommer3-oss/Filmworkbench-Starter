# Install the public node dependencies

The runnable dialogue starter uses three public projects. The historical case graphs in `graphs/` retain their original dependencies; they are not all portable replay programs.

| Project | Revision used for the starter check | Purpose |
| --- | --- | --- |
| [ComfyUI](https://github.com/Comfy-Org/ComfyUI/commit/63be2f9b82ad0dac88a7ceaa28a9cf3154125a18) | `63be2f9b82ad0dac88a7ceaa28a9cf3154125a18` (0.42.1) | H3 conditioning, sampling, attention, AV joining, video output |
| [NikoDemon80: H3 Motion Context](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context/commit/518c083d11d80fa5920222ad89889924ee4401c9) | `518c083d11d80fa5920222ad89889924ee4401c9` (0.7.1) | Save/load the S1 AV latent; trim output |
| [LBH-123-AI: H3 latent upscaler](https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler/tree/40316cf008b2fd8663263270669eb4da23f89d2c) | `40316cf008b2fd8663263270669eb4da23f89d2c` | Learned conv_v1 latent upscale |

## Fresh installation

Follow the [official ComfyUI installation guide](https://docs.comfy.org/installation/manual_install). Install a matching NVIDIA driver and CUDA-enabled PyTorch build, then ComfyUI's Python requirements. Use the Python interpreter belonging to ComfyUI for those dependencies; the starter itself needs only Python 3.11+ and FFmpeg on PATH. Python 3.12 is a reasonable choice for a new backend environment; package wheel availability must be checked on your OS.

For a **new, dedicated Git installation**, these commands select the recorded sources. Do not check out old revisions inside a working production installation. The final two custom-node projects have no requirements.txt at these revisions; they use the backend's installed libraries.

```console
git clone https://github.com/Comfy-Org/ComfyUI.git ComfyUI
git -C ComfyUI checkout --detach 63be2f9b82ad0dac88a7ceaa28a9cf3154125a18
git clone https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context.git ComfyUI/custom_nodes/ComfyUI-H3-Motion-Context
git -C ComfyUI/custom_nodes/ComfyUI-H3-Motion-Context checkout --detach 518c083d11d80fa5920222ad89889924ee4401c9
git clone https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler.git ComfyUI/custom_nodes/Comfyui_Minimax_h3_latent_Upscaler
git -C ComfyUI/custom_nodes/Comfyui_Minimax_h3_latent_Upscaler checkout --detach 40316cf008b2fd8663263270669eb4da23f89d2c
```

Install the GPU packages and `ComfyUI/requirements.txt` inside that environment, following the official guide above. ComfyUI's recorded requirements include `comfy-kitchen==0.2.39` and `comfy-aimdo==0.5.6`; omitting them can break the chosen attention backend. Check that `python -c "import torch; print(torch.cuda.is_available())"` reports `True` **in the backend environment**. Start ComfyUI with its normal launcher (or `python main.py --listen 127.0.0.1 --port 8188` from that environment). Check its console for custom-node import failures.

Get the [exact models](MODELS.md), restart or refresh the backend, and follow [Quickstart](QUICKSTART.md). A current portable ComfyUI installation can also work if `doctor.py --online` finds every required node and setting; its version is then a different test configuration.

## Why the starter no longer needs the timeline pack

The production S2 graph used OBVPM/chanon's `H3StageLatent`. The local timeline package is 0.4.3, but the public main inspected for this release exposed 0.1.4 without that node. We therefore do not prescribe it as an installable starter dependency.

In `examples/dialogue/S2.api.json`, node 22 now uses stock `LTXVConcatAVLatent`: upscaled video from node 21, unchanged S1 audio from output 1 of node 20. The Motion Context file loader supplies a mask-free AV latent; the upscaler returns a plain video tensor on CPU. Both inputs have their batch dimension. For this specific path the replacement packs the same streams without carrying an old noise mask. Temporal chunking remains enabled. This is not a blanket conversion for arbitrary masked/4D graphs. Historical graphs are retained unchanged as provenance.

## Additional historical dependencies and credits

- [roycho87: geiru_context_suite](https://github.com/roycho87/geiru_context_suite), historically installed as `clown_context_suite`, revision `c3c493ec2cfc32ccde933f81647982ee0f9546b2`: keystone/reference context in some chain examples.
- [OBVPM / chanon](https://github.com/chanon/comfyui-obvpm-timeline): two-stage work and historical stage nodes. Historical `H3StageLatent` availability is not guaranteed by installing public main.
- MiniMax H3 and the checkpoint contributors linked in [model sources](model_sources.json).

These projects and weights retain their own terms. Filmworkbench's MIT license covers its own code and documentation only. The author's personal H3 authorization does not transfer to other users. Review the model/provider terms for your intended use.
