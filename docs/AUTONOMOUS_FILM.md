# A bounded autonomous film task

The director is the tool-capable AI agent running this project, not a separate bundled language model or a background daemon. In autonomous mode the same recipe runner is used, but the commissioned agent reviews each take and can accept or reject it without asking the user every time. The client must remain active and provide the image/media inspection tools needed for the task. If it cannot inspect the required evidence, it must stop and report the missing capability.

## Commission

Example user instruction:

> Make a short film autonomously using K2 and K3, with the supplied references. Keep it to these scenes, at most three takes per stage and sixteen render submissions in total. Inspect the results, carry forward the observed state, and show me the final film with its remaining problems. Do not use paid image or voice services.

```console
python film.py init projects/my-autofilm --recipes K2 K3 --mode autonomous --max-takes 3 --max-renders 16
python film.py check projects/my-autofilm --online
```

The agent records the story, scene goals, reference roles and constraints in the project. It edits the copied S1/S2 prompts and references to match the task. A paid provider, cloud rendering or new image generation still needs the user's relevant authorization; autonomous mode is not permission to spend money.

## Agent loop

1. Read film.json, state.json, the applicable recipe pages and previous accepted assessments. For each scene, work backward from the visible result to the necessary starting state. Maintain cast, location, object ownership/count and movement. Do not repeat a completed action in the next prompt.
2. Call `film.py next PROJECT --comfy-root PATH` for the next stage. The runner uses only accepted parents. Never raise budgets or switch to an unrelated recipe merely to hide a failed result.
3. Call `film.py review PROJECT --job JOB`. This writes sampled frames, the last frame, a WAV and assessment.json alongside the full review video. S2 review uses S1 audio. Inspect the full video/audio with client tools when available; still frames alone cannot establish complete motion or spoken-word correctness.
4. Fill assessment.json with the actual observations: action, identity, continuity, motion, audio, story; cite timestamps/files. Record the observed end state and any limitations. Use pass, warning, fail, unknown or not_applicable honestly. Never generate a blanket passing assessment from technical render success.
5. For an acceptable take: `film.py accept PROJECT --job JOB --assessment PATH_TO_ASSESSMENT`. The assessment is bound to the exact take fingerprint and video hash. Missing core observations, failed checks, or a stale assessment prevent acceptance. Unchecked motion/audio must be disclosed under limitations; speech-critical or motion-critical tasks must not be accepted without the necessary review.
6. For a rejected take, retain the assessment and call `retry --job JOB`, adjust the cause and rerender within the budget. It invalidates descendants. Continue from the actual accepted result, not an assumed old state. At the budget limit, report the partial result and unresolved issue instead of increasing the budget.
7. Once every stage is accepted, assemble. Review the whole film for story order, transitions and audio, and report remaining defects. This final narrative review is done by the agent; the runner does not certify artistic quality.

The agent repeats this loop itself during the active task. There is deliberately no blind `--auto-accept` switch. Technical tests use a separate private harness and do not count as creative reviews.

## What is portable and what is not claimed

Included: planning instructions, all recipe prompt templates, own-reference mapping, S1/S2 continuation, review materials, per-take acceptance records, observed-state notes, retry limits and film assembly. A guided mode uses the same tools with the user's approvals instead.

The large private production toolkit also has specialized local critics, speech services and experimental editors. Those installations are not silently assumed on a stranger's computer. This release relies on the active agent's inspection capabilities and records gaps explicitly. It does not guarantee fully consistent worlds, correct dialogue, perfect story judgment, automatic reference generation or precise object replacement in an existing video.
