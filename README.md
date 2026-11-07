# Filmworkbench — short films from an AI chat

Eight H3 scene recipes plus a marketplace chain, with own reference images, two-pass rendering, approvals between stages and final film assembly. ComfyUI renders underneath; a tool-capable chat agent handles the project folder and discusses shot decisions with you.

**v0.1.1** · [Download the starter](https://github.com/martinsommer3-oss/Filmworkbench-Starter/releases/tag/v0.1.1) · [Example videos and reference overviews](examples/README.md) · [Validation and limits](docs/VALIDATION.md)

## Start in three sentences

Download the [starter ZIP](https://github.com/martinsommer3-oss/Filmworkbench-Starter/releases/download/v0.1.1/Filmworkbench-v0.1.1-starter.zip), extract it and open the folder in Codex, Claude Code or another agent with file and terminal access. Paste the prompt below; the agent checks your setup and helps prepare your film with supplied or own images. The optional [example-video ZIP](https://github.com/martinsommer3-oss/Filmworkbench-Starter/releases/download/v0.1.0/Filmworkbench-v0.1-examples.zip) adds all ten finished videos to the same folder.

> Read AGENTS.md and filmworkbench.json. Help me make a short film using these recipes and my pictures. Check my setup, agree the scene plan with me, and stop for my approval after each rendered stage.

## What is executable

Choose one of [three gates](docs/GATES.md): one image/clip, a guided film with your approvals, or a bounded autonomous task reviewed by the active agent. Image generation uses your configured provider; video generation uses the local backend.

All [eight recipes](recipes/README.md) and MARKET can be selected with `film.py`: K1 dialogue, K2 reverse angle, K3 leave/changed-state return, K4 establishing shot with dialogue prelap, K6 spacecraft/cockpit, K7 character entrance, K8 lake creature, K9 doorway traversal, and the combined marketplace example. The runner generates their predecessor latents on your machine, keeps S1 and S2 parents separate, and stops for acceptance after each stage.

```console
python film.py init projects/my-film --recipes K2 K3
python film.py check projects/my-film --online
python film.py next projects/my-film --comfy-root "C:/AI/ComfyUI"
```

Follow [guided filmmaking](docs/GUIDED_FILM.md) for review, acceptance, retries, own images/prompts and assembly. A film can combine several recipe scenes with hard cuts. Their images and prompts must describe the same cast, places and changed states; the runner does not invent continuity between scenes. The original `render_example.py` remains available as a smaller first-clip test.

## Setup

- [Exact stack](docs/STACK.md), [public node installation](docs/DEPENDENCIES.md), [model downloads and hashes](docs/MODELS.md).
- Python 3.11+, FFmpeg with libx264 and drawtext, and a working local ComfyUI GPU backend.
- For all recipes: the seven documented model files and public Motion Context, LBH latent upscaler and geiru_context_suite nodes. No private node is required by the adapted graphs.
- `python setup_models.py --comfy-root YOUR_COMFY_ROOT --all` plans the model setup; `--download` explicitly downloads and `--verify` verifies installed bytes.
- `film.py check PROJECT --online` reports missing nodes/models and incompatible settings before any render.

GPT Image is recommended for new reference sets; local Krea 2 is the image fallback. Neither is needed to try the supplied examples. Chat media previews depend on the client. Image generation uses the client's available tools or a separately configured service; it is not installed by this package.

## Method and limits

Prepare what the camera will need to see: characters, room views and changed prop states. Give H3 manageable actions. Motion Context carries the preceding accepted AV latent, and the repeated context is trimmed before assembly. The base model is H3 Hybrid fl2va/ref2va b25–49 INT8. S1 is 864×480; learned latent upscale and DMAD refinement produce S2 at 1952×1088. The final film uses S1 audio.

This release implements **guided filmmaking and bounded agent-directed autonomy**, including full recipe chains and own inputs. In [autonomous mode](docs/AUTONOMOUS_FILM.md), the active agent reviews and accepts takes with evidence and attempt limits. It does not bundle a separate LLM, the private specialist critic services, automatic world-view generation or precise object-level video editing. World-state continuity, voices, background drift and story judgment still need review. These are selected worked recipes, not universal reliability guarantees.

The tested workstation uses Windows and an RTX 5090 with 32 GB VRAM and 128 GB system RAM. A fresh GPU/backend installation and lower-memory machines remain untested. See [validation](docs/VALIDATION.md) for the actual release checks.

The gallery contains finished S2 examples, actual reference/workflow overviews and render records one level below. Speaking examples have English subtitles over their original German audio. New films need their own subtitle text/timing.

Our separate [editing notes](docs/EDIT_NOTES.md) summarize tested repairs and unresolved cases; the specialized edit tools are not bundled.

## Credits and terms

Our own code/docs are [MIT](LICENSE). Models, third-party nodes and generated media retain their own terms. No model weights, upstream node implementation code, private chats or production history are bundled. [Component credits](docs/CREDITS.md) · [Media notes](docs/MEDIA.md).
