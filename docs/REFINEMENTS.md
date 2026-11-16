# Planning and finishing refinements

Use the [introduction and quickstart](QUICKSTART.md) to run the starter. These refinements are useful when you adapt a recipe for your own film.

## Five planning profiles

Pick the genre and visual treatment separately. The table suggests a scene to build and the moment a viewer should be able to identify. Start with a short, complete story and select recipes for the shots it needs.

| Genre | One visual starting point | What to plan and check |
| --- | --- | --- |
| Psychological drama | Live action | Make two conflicting wants visible. Let a line or a familiar prop change the situation, show the listener's reaction, then give them a visible decision. Try K1 or K2. |
| Horror or psychological thriller | Live action | Escalate two recognizable warning signs. Hold a shot to build anticipation, then make the threat and the character's response legible. Try a K9 reveal. |
| Science-fiction mystery | Live action | Put one strange object or phenomenon at the center of the plot. End on a reveal that changes how the viewer reads an earlier clue. Try K6 for the setting or K3 for a changed prop. |
| Fantasy action | Anime | Establish the stakes and each character's position. Keep an important action and its consequence readable, and show the cause of the reversal before the outcome. Try K7 to bring a character into the action. |
| Comedy | Stylized 3D animation | Set an expectation, break it with a concrete action or line, then hold on the reaction long enough for the joke to register. Try K1 with a reaction close-up. |

For camera prompts, name the move, how far it travels and its pace. A physical push-in changes the viewpoint, whereas an optical zoom changes the framing from the same position. Over-the-shoulder framing, overhead views, inserts and slow forward or backward moves were among the stronger results in a small first-pass test.

If a particular cut needs a reference image, attach your own image in the appropriate recipe slot. In the prompt, name the reference and specify the shot it anchors. For dialogue that continues across an internal cut, see `<scenetrans>` in the [official MiniMax H3 prompt guide](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/base-en.txt). These are planning options backed by small S1 tests. Review the actual shot change, delivery and synchronization.

## Compensate early cuts in continuation prompts

Set `"compensate_continuation_cuts": true` on the scene in `film.json` before rendering your edited prompts. Write the desired cut in **raw-clip time**, including the 56-frame context head, on a line beginning `[Shot 2] At 00:05.000,`. The scene editor keeps that original mark. When building the submitted S1 graph, the runner shifts eligible marks by eight frames, so this example is sent as `00:05.333`.

This applies to 226- and 345-frame S1 continuation graphs with a 56-frame context head, at least two seconds into the delivered clip. A mark that would shift past the last frame stays in place. The runner preserves cut order. Compare the render against your original planned time after subtracting the context. The option is off by default for archived recipe replay and existing projects. Changing it after an S1 submission invalidates the affected work under the normal retry checks.

In development, 31 of 32 cuts in two sets of quiet continuation clips landed within 0.25 seconds after compensation. The measurement covers S1, two clip lengths and a small set of scenes. Check your own genres, movement and dialogue.

## Smooth an ambience seam

After listening to the accepted stages, add the IDs of incoming continuation parts to `ambience_bridge_parts` on the scene in `film.json`. For example, `"ambience_bridge_parts": ["MARKET_G3"]` would select the join into `MARKET_G3` if you verify that this take has only ambience for up to 1.5 seconds on each side. Use the part IDs under the scene's `assembly.parts`. Only select joins you have listened to.

Run `python film.py assemble PROJECT`. The runner uses exact frame counts for join positions, preserves S1 audio as the source, and blends a quiet reflected tail into the start of the follow-up. An incoming transient shortens the bridge or causes it to be skipped. The tool also skips joins with too little quiet outgoing audio. The assembly report records what was applied or skipped. Hard scene cuts and scenes with an explicit audio prelap are excluded.

Use the bridge only for steady ambience. Leave a join out when it contains speech, music, distinctive footsteps or rhythmic sound. Listen to the result with its surrounding shots. Removing the ID and assembling again gives you the ordinary join.
