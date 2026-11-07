# Filmworkbench — v0.1 starter kit

Scene recipes and a small two-pass MiniMax H3 runner for people who want to make short films through an AI chat or a command line.

This first package shares eight worked scene cases plus the marketplace case, their selected S2 examples, actual API graphs, reference stills and known limits. It also includes a runnable first-clip dialogue example. The broader Filmworkbench project has guided and autonomous film workflows; this starter does **not** yet package that complete orchestration system or a one-click installer.

**v0.1.0 — development starter.** [Download the release](https://github.com/martinsommer3-oss/Filmworkbench-Starter/releases/tag/v0.1.0) · [Watch the examples](examples/README.md) · [Exact stack and requirements](docs/STACK.md). The first-clip S1→S2 path was tested from an extracted release package on an existing RTX 5090 backend; see [validation](docs/VALIDATION.md).

## New to GitHub or using an AI agent?

Download the [starter ZIP](https://github.com/martinsommer3-oss/Filmworkbench-Starter/releases/download/v0.1.0/Filmworkbench-v0.1-starter.zip) and extract it into a new folder; the optional [examples ZIP](https://github.com/martinsommer3-oss/Filmworkbench-Starter/releases/download/v0.1.0/Filmworkbench-v0.1-examples.zip) adds all ten videos to that same folder. Open the folder as a project in Codex, Claude Code or another agent with local file/terminal access, then paste the prompt below. The agent can check your machine, explain what is missing and help you run the supplied example.

> Read AGENTS.md and filmworkbench.json. Check this machine for the dialogue starter, explain any missing models or nodes, and help me run its S1–S2 workflow using the included reference images. Show me the setup steps before downloading models or starting a render.

## Start here

1. Browse the [workflow example gallery](examples/README.md): video and overview first, render data one level below. Read the [eight recipes](recipes/README.md). Each describes preparation, what worked and what still fails.
2. Extract `Filmworkbench-v0.1-examples.zip` beside this README. It places each `video_S2.mp4` beside its overview under `examples/<case>/`. All eight scene cases are S2, with a visible MiniMax H3 credit. English subtitles are burned into the six cases with German dialogue; two require no dialogue translation. The pack also contains the English-subtitled marketplace and Fantasy films.
3. Inspect the [Fantasy making-of](docs/fantasy_reference_overview.png), showing the actual references and rendering path for “The Last Light.” Its English-subtitled video and actual image references are included.
4. Try the [two-pass dialogue starter](docs/QUICKSTART.md) after following the [node installation](docs/DEPENDENCIES.md) and [model download guide](docs/MODELS.md). You can ask your tool-capable agent to read this folder and explain the recipe before running it.

```console
python doctor.py
python doctor.py --online
python render_example.py
```

The included `setup_models.py` can plan downloads, explicitly fetch the exact weights and verify their SHA-256 values. The doctor checks included assets, and with `--online` reads installed nodes, model filenames and supported settings without generating anything. Use `--all` to inspect all 44 case graphs. The starter also verifies its graph links offline. A render needs the explicit `--run` option.

GPT Image is the recommended source for new reference sets (`$imagegen` in a supported Codex client); Krea 2 is the local fallback. Access options and limits are explained in the [technical overview](docs/STACK.md). Neither is required to rerender the included starter because its input pictures are supplied. See [reproduction and portability](docs/REPRODUCTION.md).

## What the recipes do

Prepare the visible information a shot needs, keep each action manageable, and continue from the accepted result. A wide establishes people and props; close-ups show action and reaction. An opposite view supplies what the original camera cannot see. A changed prop needs a changed input state.

Motion Context carries the preceding audio/video latent across clip boundaries. The repeated context is trimmed. This is different from dissolving two unrelated clips, and it does not create persistent world memory. Wide returns are useful for the selected examples, not mandatory at every join in every future film.

The example runner uses the historical H3 Hybrid b25–49 INT8 checkpoint, S1 at 864×480, learned latent upscale and DMAD S2 refinement at 1952×1088. It copies S1 audio under the S2 picture. Dependencies retain their own licenses and access requirements; model weights are not included.

## Scope and limits

- These are selected successes with documented problems, not eight universally reliable presets or a success-rate benchmark.
- The exported case graphs are ComfyUI API JSON, not visual-editor canvas layouts. The runnable starter has all its stills; full chains also need generated predecessor latents and manual decisions.
- Models, nodes and ComfyUI versions affect compatibility and results. Exact bitwise reproduction is not promised.
- The original workstation was Windows with an RTX 5090. Lower-memory systems and fresh installations have not been validated for this package.
- Automatic story judgment, long-chain drift, voices and world-state continuity remain open work.

## Credits and terms

See [component credits](docs/CREDITS.md) and [dependency installation](docs/DEPENDENCIES.md). Filmworkbench's own code and original documentation use the [MIT license](LICENSE), as approved by the project owner. The MIT license does not relicense third-party code, models or generated media. See [media notes](docs/MEDIA.md).

Browse the [video and reference index](examples/README.md). The code and videos are hosted on GitHub; see [distribution layout](docs/DISTRIBUTION.md).
