# Three ways to use the workbench

The same tool-capable agent routes the request. Codex, Claude Code or a local agent can do this if the client provides file access, command execution and the media inspection needed by the task. A chat-only text model cannot operate the renderer by itself.

## Gate 1 — one image or clip

For one image, use the client's configured image generator: GPT Image is the recommended reference-image route; local Krea 2 is the fallback. Neither service is installed by this repository. If unavailable, the agent should explain what is missing; supplied references also work without an image generator.

For a supplied single-clip example, use `python render_example.py --run --comfy-root PATH`. It produces the first dialogue clip through S1 and S2, using S1 audio. For a custom clip, initialize a K1 project with `film.py`, edit its copied references and first paired prompt files, run `check --online`, then `next` once. Present that S1 clip and stop; no full film is required. If the user wants refinement, follow the first S2 stage after their acceptance. Include the MiniMax H3 credit when preparing a shareable export.

Example: "Make one short dialogue clip from these two character images and this room view. Show me S1 first."

## Gate 2 — guided film

Agree the story, shots, references and relevant states with the user. Select and adapt recipes, render one stage, show it, and wait for the user's decision. Continue from accepted results, then assemble. Follow [guided filmmaking](GUIDED_FILM.md).

Example: "Help me plan a short film using dialogue, a reverse angle and a return to the changed room. Ask before continuing after each stage."

## Gate 3 — bounded autonomous film

The user commissions the active agent to plan and carry out a limited film task. The agent reviews each take, records evidence and the observed end state, accepts or retries within the agreed budget, and assembles the result. Follow [autonomous filmmaking](AUTONOMOUS_FILM.md). The runner is not a separate autonomous LLM service; the client's agent performs these decisions.

Example: "Make a short film autonomously with the supplied K1 references. Allow up to three takes per stage and eight render submissions. Inspect the results and show the finished film with its remaining problems. Do not use paid services."

All three routes require the stated tools and dependencies. Missing media-inspection capabilities must be disclosed; technical render completion alone is not creative approval. Editing experiments are summarized separately in [edit notes](EDIT_NOTES.md).
