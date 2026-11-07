# Credits and upstream projects

Filmworkbench combines existing model/node work with a project-folder workflow and worked scene recipes. Thanks to the authors below. Their implementations and weights are **not vendored** here; use their original repositories and terms.

| Contributor / project | Used for | Original source |
| --- | --- | --- |
| MiniMax H3 / Comfy-Org | Base H3 components, conditioning, sampling and stock AV/video nodes | [H3 weights](https://huggingface.co/Comfy-Org/MiniMax-H3) · [ComfyUI](https://github.com/Comfy-Org/ComfyUI) |
| smhfacct | Hybrid fl2va/ref2va b25–49 INT8 checkpoint | [Hybrid weights](https://huggingface.co/smhfacct/Minimax-H3-fl2va-ref2va-hybrid-models) |
| Kijai | Published DMAD rank-39 LoRA file used by the recipe | [Experimental H3 weights](https://huggingface.co/Kijai/MiniMax-H3-experimental) |
| lightx2v | Turbo-8 continuation LoRA | [Turbo weights](https://huggingface.co/lightx2v/Minimax-h3-Turbo) |
| NikoDemon80 | Motion Context, AV latent save/load and context trimming | [H3 Motion Context](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context) |
| LBH-123-AI | Learned latent upscale implementation and checkpoint | [Nodes](https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler) · [Weights](https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler) |
| roycho87 | Context/keystone nodes used in historical chains | [geiru_context_suite](https://github.com/roycho87/geiru_context_suite) |
| OBVPM / chanon | Timeline and two-stage workflow work informing the production setup; historical stage helper | [Timeline project](https://github.com/chanon/comfyui-obvpm-timeline) · [u/obvpm's workflow post](https://www.reddit.com/r/StableDiffusion/comments/1x4z41u/updated_obvpm_timeline_workflow_v014007/) |

Also thanks to [u/xyzdist's degradation discussion](https://www.reddit.com/r/StableDiffusion/comments/1x0nbr5/h3_degradation_my_turn_attempts_to_fixing/) and [H3-LongTakeNoCuts](https://github.com/xyzDist/H3-LongTakeNoCuts) for useful investigation of long-chain failure modes. That project is research background here, **not a required node pack in the supplied starter**. We do not attribute the whole continuation method to a single discussion or claim its experiments solved continuity.

The runnable first-clip graph uses only ComfyUI, H3 Motion Context and LBH's upscaler. Historical case graphs retain their original node references. The local timeline helper was replaced in the runnable starter so it does not depend on a newer local timeline package. See [installation and exact revisions](DEPENDENCIES.md).

Own code/docs: [MIT](../LICENSE). Models, external software, provider skills and generated media keep their respective terms. See [media notes](MEDIA.md). No endorsement by these authors is implied.

The full film.py chain runner additionally uses the public geiru_context_suite keystone. It adapts the archived stage joins to stock AV concatenation without distributing upstream node code.
