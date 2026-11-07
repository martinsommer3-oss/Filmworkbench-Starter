# Make a film through your chat agent

Open this folder in a tool-capable agent. Ask it to read AGENTS.md, discuss the film, prepare the references and select recipes. All eight scene recipes and MARKET have executable chains. A film can combine multiple recipes with hard cuts; continuity inside a recipe uses its recorded latent links. Cross-scene identity and changed states are prepared in the references and prompts, not inferred by the runner.

## Three short steps

1. Download the starter ZIP, extract it and open that folder in your agent.
2. Paste: "Read AGENTS.md. Help me make a short film using these recipes and my pictures. Check my setup, agree the scene plan with me, and stop for my approval after each rendered stage."
3. The agent helps install missing public nodes/models, prepares your film folder and shows each result before continuing.

A local ComfyUI GPU backend is required for rendering. The agent itself may be local or cloud-based. Inline media display depends on your chat client; the CLI prints the exact video file to open.

## Create and inspect a project

```console
python film.py init projects/my-film --recipes K2 K3 MARKET
python film.py check projects/my-film
python film.py check projects/my-film --online
python film.py status projects/my-film
```

The recipe choices are K1, K2, K3, K4, K6, K7, K8, K9 and MARKET. Repeat a recipe to use it for another scene. The missing K5 number is historical, not a missing ninth scene. You can start with one recipe, or choose all scenes at initialization. To change the scene list later, initialize a new project and copy your edited references/prompts into it.

`film.json` lists the scenes, reference mappings, per-stage prompt files, seeds and assembly decisions. Each scene gets its own copy of the supplied inputs. No private production paths or predecessor files are needed. Generated predecessors are saved in a fresh namespace on your own backend.

## Use your own images, voices and prompts

Copy your files inside the new project folder. In each scene's `assets` mapping, change the value (a project-relative filename) while keeping the original key. One asset key may feed several graphs; replacing it updates all those uses in that scene. Consult the recipe page and reference overview to distinguish character portraits, full bodies, room views, start guides, opposite views and changed-state images.

Edit the text files listed under `prompts` for the intended action, characters, picture numbering and spoken dialogue. S1 and S2 have separate recorded prompts: update both for a custom clip, preserving their reference ordering and technical roles. Keep the reference family coherent; merely replacing a picture cannot make an unchanged prompt describe a different film. Seeds are explicit in `film.json`. File lengths and graph topology remain the selected recipe's defaults.

For K4, `assembly.prelap` defines the external WAV and its placement in seconds. Replace that WAV through the same assets mapping when changing the dialogue; adjust its start/end to fit the new cut. This supplied audio is mixed over the establishing shot. The runner does not synthesize replacement speech or translate new dialogue automatically.

For image preparation, use GPT Image where supported or your own local Krea 2 installation. The supplied recipes need neither generator to rerender their included references. New reference sets need spatial and state review before video generation.

## Render, review, approve

```console
python film.py next projects/my-film --comfy-root "C:/AI/ComfyUI"
python film.py status projects/my-film
python film.py accept projects/my-film --job 01_K2/K1_A1_S1 --note "User approved composition and action"
python film.py next projects/my-film --comfy-root "C:/AI/ComfyUI"
```

`next` runs exactly one S1 or S2 stage and stops. It never accepts a result. Use the actual job name from `status`, not a guessed name. Review S1 for action and continuity, then S2 for refinement. The S2 review file and final film both use S1 audio. Continue until every stage is accepted, then:

```console
python film.py assemble projects/my-film
```

The result appears under the project's `exports/` directory with a provenance record and visible MiniMax H3 credit. Graphs trim their repeated motion context already; assembly does not trim it twice. S1 audio is paired with each S2 segment, K4 prelap is applied, and recipe scenes are joined in plan order. All files are retained.

## Reroll, changed inputs and interruption

```console
python film.py retry projects/my-film --job 01_K2/K1_A1_S1
```

This retains previous files and archives the state, but invalidates that stage and every later stage in the film. Edit the desired prompt, image or seed and call `next`. Descendants must be rebuilt from the newly accepted result. Changing an already-rendered input without `retry` is refused; this also catches changed image contents at the same filename.

A client timeout does not cancel the server's GPU job. Use `recover --job JOB` after it completes to import its successful history; never blindly resubmit. For a failed render, inspect its saved history and use `retry` only after the backend is idle. A crashed controller may leave `.film.lock`; remove that lock file only after verifying that no controller is still running. Keep one controller and one GPU producer at a time.

`--server` selects a local backend address; `--model-map` explicitly maps canonical model filenames to installed subdirectories. `check --online` reports missing node classes, model files and incompatible settings. Use `setup_models.py --all` to include Turbo-8 for the complete recipe set.

## Scope

This is guided recipe-based filmmaking with user approvals, own inputs, repeatable continuations and final assembly. For bounded agent-directed autonomy, see [autonomous mode](AUTONOMOUS_FILM.md). It does not install a separate story critic, automatic multi-view image generation, arbitrary cross-recipe latent splicing or object-level video repair. The agent handles planning and discusses the observed state with the user. The executable runner enforces dependencies and approvals; it does not judge creative quality.
