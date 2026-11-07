# What runs where

## Choose the task first

| What you want | What you need |
| --- | --- |
| Watch the ten finished examples | A browser or video player; no models, GPU or AI subscription |
| Study prompts, references and settings | This repository; no rendering setup |
| Rerender the first dialogue clip | Python 3.11+, FFmpeg, a working local ComfyUI GPU backend, two public custom-node packs and the six exact starter weights below |
| Make new reference images | GPT Image through a supported client/service, or your own local Krea 2 setup; not needed for the supplied starter |
| Rebuild a full historical chain | The recorded predecessor latents must be generated in order; additional historical nodes and assembly decisions may be needed; no full-chain runner is shipped |
| Run the full guided/autonomous film director | Not included in v0.1 |

The runnable example uses **H3 Hybrid fl2va/ref2va b25–49 INT8**, not the standalone Ref2VA checkpoint. `MiniMaxH3ReferenceToVideo` is the conditioning node; seeing that node in the graph does not mean a different base checkpoint was loaded.

## Exact weight variants

| Component | Quantization / precision | Purpose |
| --- | --- | --- |
| [hybrid](https://huggingface.co/smhfacct/Minimax-H3-fl2va-ref2va-hybrid-models/blob/6328c7dc34369783dd6a224b366aeb698e552e19/minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors) | INT8 | H3 Hybrid fl2va/ref2va, b25–49; shared video generator for S1 and S2 |
| [text_encoder](https://huggingface.co/Comfy-Org/MiniMax-H3/blob/3f57e8291d2ef846f9a074b1b76d2767db434abe/text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors) | INT8 convrot | Qwen3-VL 32B H3 text/vision conditioning encoder; not the chat agent |
| [video_vae](https://huggingface.co/Comfy-Org/MiniMax-H3/blob/7a2065e37f5ff9d3c4e605f164d4cac388eff8e8/vae/minimax_h3_video_vae_int8_convrot.safetensors) | INT8 convrot | Encode/decode H3 image and video latents |
| [audio_vae](https://huggingface.co/Comfy-Org/MiniMax-H3/blob/3f57e8291d2ef846f9a074b1b76d2767db434abe/vae/minimax_h3_audio_vae_fp32.safetensors) | FP32 | Encode/decode H3 audio latents |
| [dmad](https://huggingface.co/Kijai/MiniMax-H3-experimental/blob/1db9d50082f491fb5b2fbbee7499fb93e9190c51/loras/minimax_h3_DMAD_4step_full_lora_avg_rank_39_bf16.safetensors) | BF16 | DMAD rank-39 distillation LoRA; first-clip S1 and S2 refinement |
| [turbo8](https://huggingface.co/lightx2v/Minimax-h3-Turbo/blob/a29e57d195f80ead07c89f89e55ecf2911e893c5/minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors) | BF16 | Turbo-8 ref2v LoRA; selected continuation recipes, not the standalone first clip |
| [upscaler](https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler/blob/6749d7b4376fe1597115c4807f0f659c426d0b4d/minimax_h3_latent_upscaler_3d_conv_v1/minimax_h3_latent_upscaler_3d_conv_v1_fp16.safetensors) | FP16 | Learned conv_v1 latent upscaler between S1 and S2 |

[Download guide](MODELS.md) · [Machine-readable filenames, revisions, hashes and sizes](model_sources.json)

The dialogue starter uses DMAD at strength 1.0 in both passes. Despite `4step` in the LoRA filename, this particular S1 graph runs **8 steps**, `er_sde`, beta schedule, denoise 1.0 at **864×480**. S2 runs **2 steps**, `er_sde`, linear_quadratic schedule, denoise **0.4** at **1952×1088**. The graph also records Comfy Kitchen attention and the sparse-attention settings. The source graphs are authoritative; these are not global defaults for every historical case.

The upscaler operates on the saved S1 video latent with temporal chunking enabled. The starter combines that upscaled video with S1 audio using stock ComfyUI AV nodes, refines the picture, and copies the original S1 audio into the final MP4.

## Nodes and joins

The runnable starter needs **ComfyUI plus two custom-node projects**: NikoDemon80's H3 Motion Context and LBH-123-AI's H3 latent upscaler. Exact revisions and installation commands are in [DEPENDENCIES.md](DEPENDENCIES.md). There is no private custom node required by the starter.

For continuation, the broader recipes feed the preceding accepted AV latent into Motion Context and trim the repeated context frames. Some historical graphs also use a front keystone from roycho87's context pack. Those joins preserve motion context; they do not provide permanent world-state memory. Historical graphs still mention OBVPM's stage helper; the tested standalone S2 graph replaces it with stock `LTXVConcatAVLatent`.

## Memory and alternatives

The verified configuration was Windows, RTX 5090 with **32 GB VRAM**, and **128 GB system RAM**. The six weights occupy 52.6 GB on disk, which is not a VRAM requirement. Lower VRAM/RAM configurations have not been validated for this release.

Do not silently swap in a different checkpoint or quantization. Offloading, smaller/shorter clips or other quantizations are possible experiments, but this release has no tested low-memory preset to recommend. They may change speed, conditioning, output quality or node compatibility. Start with the doctor and the exact model manifest; document any alternative as a separate configuration.

## Reference images

We use GPT Image through Codex's **`$imagegen`** skill when the client exposes built-in image generation. With an eligible signed-in plan, built-in generations use the plan's usage allowance; availability and limits depend on the client/account. API-key workflows use API billing instead. A skill by itself does not provide model access. See the official [image-generation instructions](https://learn.chatgpt.com/docs/image-generation) and [usage/pricing guide](https://learn.chatgpt.com/docs/pricing).

You can also create references in ChatGPT or another supported online service and save the resulting files into your project. The [OpenAI image API](https://developers.openai.com/api/docs/guides/image-generation) is a separate programmatic route. Krea 2 is the local image fallback used in the wider project; its generator/model installation is not part of this first-clip starter. No paid image call is made by the supplied tools.

All starter references are already included. For a new sequence, use a consistent set of cast and location references and review the opposite views and changed object states before rendering.

## What is distributed

Our own runner, setup checker, recipe graphs/settings, documentation and selected generated media are distributed. **No third-party model weights, custom-node implementations, provider skills or private production history are bundled.** Dependencies are linked to their original GitHub/Hugging Face sources and downloaded there explicitly. Our MIT license does not relicense those dependencies or generated media. See [credits](CREDITS.md) and [media terms](MEDIA.md).
