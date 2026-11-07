# Get the exact model files

The dialogue starter needs six files: **52.6 GB decimal** in total. The optional Turbo-8 continuation LoRA brings all seven to **54.5 GB**. Model weights are downloaded from their publishers, not included in this release.

The helper retains a download staging copy for resumability and verifies the installed copy. Allow roughly **110 GB free for weights plus staging**, with additional room for the backend, latents and outputs. This is disk space, not VRAM. The tested workstation has an RTX 5090 with 32 GB VRAM and 128 GB system RAM. A lower-memory configuration is not validated by this release.

## Guided download

From the release folder, use your Python 3.11+ environment:

```console
python -m pip install -U huggingface_hub
python setup_models.py --comfy-root "C:/AI/ComfyUI"
python setup_models.py --comfy-root "C:/AI/ComfyUI" --download
python setup_models.py --comfy-root "C:/AI/ComfyUI" --verify
```

The first helper call only prints a plan. `--download` invokes `hf download` for each exact file and revision, checks size and SHA-256, then copies it into the proper model category. It refuses to overwrite a differing existing file. An interrupted target copy is kept for inspection and will fail the next hash check; move it aside before retrying. Downloads remain under `ComfyUI/.filmworkbench-downloads/` unless `--cache` selects another directory. No authentication credentials are read by this helper; Hugging Face's own CLI handles any account/access requirements. Do not put tokens in this repository.

Add `--all` to include Turbo-8 for continuation cases. It is not needed for the first dialogue clip. Downloading it does not turn the historical chains into an automated replay system.

## Files and destinations

All destinations below are relative to your ComfyUI root. Each link points to an immutable source revision. Exact byte counts and SHA-256 values are in [model_sources.json](model_sources.json).

| Component | File source | Install folder |
| --- | --- | --- |
| hybrid  | [minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors](https://huggingface.co/smhfacct/Minimax-H3-fl2va-ref2va-hybrid-models/blob/6328c7dc34369783dd6a224b366aeb698e552e19/minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors) | `models/diffusion_models/` |
| text_encoder  | [qwen3vl_32b_minimax_h3_int8_convrot.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/blob/3f57e8291d2ef846f9a074b1b76d2767db434abe/text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors) | `models/text_encoders/` |
| video_vae  | [minimax_h3_video_vae_int8_convrot.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/blob/7a2065e37f5ff9d3c4e605f164d4cac388eff8e8/vae/minimax_h3_video_vae_int8_convrot.safetensors) | `models/vae/` |
| audio_vae  | [minimax_h3_audio_vae_fp32.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/blob/3f57e8291d2ef846f9a074b1b76d2767db434abe/vae/minimax_h3_audio_vae_fp32.safetensors) | `models/vae/` |
| dmad  | [minimax_h3_DMAD_4step_full_lora_avg_rank_39_bf16.safetensors](https://huggingface.co/Kijai/MiniMax-H3-experimental/blob/1db9d50082f491fb5b2fbbee7499fb93e9190c51/loras/minimax_h3_DMAD_4step_full_lora_avg_rank_39_bf16.safetensors) | `models/loras/` |
| turbo8 (optional) | [minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors](https://huggingface.co/lightx2v/Minimax-h3-Turbo/blob/a29e57d195f80ead07c89f89e55ecf2911e893c5/minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors) | `models/loras/` |
| upscaler  | [minimax_h3_latent_upscaler_3d_conv_v1_fp16.safetensors](https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler/blob/6749d7b4376fe1597115c4807f0f659c426d0b4d/minimax_h3_latent_upscaler_3d_conv_v1/minimax_h3_latent_upscaler_3d_conv_v1_fp16.safetensors) | `models/latent_upscale_models/` |

Do not substitute a similarly named quantization, a different Hybrid block range, BF16 for FP16, or a Turbo variant merely to satisfy the filename check. Those are new configurations requiring validation.

## Manual HF CLI alternative

These commands download into staging, not directly into ComfyUI. Preserve the exact remote subdirectories, then copy the downloaded file to the install folder above and run the verifier. The helper performs that flattening automatically.

```console
hf download smhfacct/Minimax-H3-fl2va-ref2va-hybrid-models minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors --revision 6328c7dc34369783dd6a224b366aeb698e552e19 --local-dir "downloads/hybrid"
hf download Comfy-Org/MiniMax-H3 text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors --revision 3f57e8291d2ef846f9a074b1b76d2767db434abe --local-dir "downloads/text_encoder"
hf download Comfy-Org/MiniMax-H3 vae/minimax_h3_video_vae_int8_convrot.safetensors --revision 7a2065e37f5ff9d3c4e605f164d4cac388eff8e8 --local-dir "downloads/video_vae"
hf download Comfy-Org/MiniMax-H3 vae/minimax_h3_audio_vae_fp32.safetensors --revision 3f57e8291d2ef846f9a074b1b76d2767db434abe --local-dir "downloads/audio_vae"
hf download Kijai/MiniMax-H3-experimental loras/minimax_h3_DMAD_4step_full_lora_avg_rank_39_bf16.safetensors --revision 1db9d50082f491fb5b2fbbee7499fb93e9190c51 --local-dir "downloads/dmad"
hf download lightx2v/Minimax-h3-Turbo minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors --revision a29e57d195f80ead07c89f89e55ecf2911e893c5 --local-dir "downloads/turbo8"
hf download LBH-123-AI/Minimax_h3_latent_Upscaler minimax_h3_latent_upscaler_3d_conv_v1/minimax_h3_latent_upscaler_3d_conv_v1_fp16.safetensors --revision 6749d7b4376fe1597115c4807f0f659c426d0b4d --local-dir "downloads/upscaler"
```

## Existing models in subdirectories

If the same verified file is already in a model subdirectory, create a JSON map using the exact relative path reported by ComfyUI's loader. Example:

```json
{
  "minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors": "H3/minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors"
}
```

Pass `--model-map model-map.json` to `setup_models.py`, `doctor.py` and `render_example.py`. Values are relative to their category, e.g. `models/diffusion_models`, not to the whole repository. The runner never guesses or silently substitutes a model. For files registered via ComfyUI's `extra_model_paths.yaml`, point the verifier to the actual category directory, for example `--model-root "loras=D:/SharedModels/loras"`. Repeat for other categories. This does not edit ComfyUI configuration. The loader must already expose the chosen filename. A filename match alone is not a hash check.

## New reference images

The starter includes every reference image it needs. No GPT Image API key, paid image service or Krea 2 download is needed for the first run. For new scenes we recommend GPT Image through `$imagegen` in a supported Codex client, ChatGPT or another supported service (see [access options](STACK.md)); Krea 2 is the local fallback. Image generation is not installed or invoked by this small starter. The larger image-generation integration and its own exact Krea model/node setup are outside v0.1's runnable scope.

Source-file pages and published hashes were checked on 7 November 2026. Bulk downloading all weights from a clean internet-connected machine was not tested in the release-building environment; its outbound Python network access was blocked. The download helper has failure-path tests, and local full-file verification is recorded separately in VALIDATION.md.
