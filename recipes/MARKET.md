# Marketplace — a more demanding combined case

[Video and workflow overview](../examples/MARKET/README.md)

[Watch the English-subtitled S2 example](https://github.com/martinsommer3-oss/Filmworkbench-Starter/releases/download/v0.1.0/Filmworkbench_MARKET_S2.mp4).

Four connected clips: arrival, buying an apple, a camera orbit, departure. The selected S1 sequence received positive user feedback; this is not a separate approval of every S2 detail. Its 1,144 story frames run for 47.67 seconds; the subtitled S2 export includes a two-second credit.

## Prepare what the camera will reveal

Supply a portrait and full-body view for each main character, coherent empty north/south/east/west views, and one populated aerial opening guide. The wide views already contain the landmarks and routes that later shots need. They do not encode a complete persistent 3D world. Background extras in this historical example had no individual identity references.

Start with the free arrival. Continue from the actual accepted AV latent using 56 video context frames and 18 audio context frames, with a first-clip front keystone. Preserve the apple's new owner and the other changed states. Use four empty location views for the orbit and departure. The main chain uses no additional Studio Memory, no MP4 reference and no imposed end images at its joins.

## Exact inputs and render data

The companion bindings files identify nine included image inputs and two synthetic voice samples (owner confirmed permission to share). Graphs contain the real prompts, seeds, node connections, sampling and upscale settings. Reference metadata is inspected separately from the graphs; no private chat history is included.

| Clip | Stage | Seed | API graph | Settings and parent hashes |
|---|---|---:|---|---|
| G1 | S1 | 71101 | [graph](../graphs/MARKET_G1_S1.api.json) | [render record](MARKET_G1_S1.render.json) |
| G1 | S2 | 71101 | [graph](../graphs/MARKET_G1_S2.api.json) | [render record](MARKET_G1_S2.render.json) |
| G2 | S1 | 71102 | [graph](../graphs/MARKET_G2_S1.api.json) | [render record](MARKET_G2_S1.render.json) |
| G2 | S2 | 71102 | [graph](../graphs/MARKET_G2_S2.api.json) | [render record](MARKET_G2_S2.render.json) |
| G3 | S1 | 71311 | [graph](../graphs/MARKET_G3_S1.api.json) | [render record](MARKET_G3_S1.render.json) |
| G3 | S2 | 71311 | [graph](../graphs/MARKET_G3_S2.api.json) | [render record](MARKET_G3_S2.render.json) |
| G4 | S1 | 71413 | [graph](../graphs/MARKET_G4_S1.api.json) | [render record](MARKET_G4_S1.render.json) |
| G4 | S2 | 71413 | [graph](../graphs/MARKET_G4_S2.api.json) | [render record](MARKET_G4_S2.render.json) |

Hybrid b25–49 INT8; S1 864×480, eight steps, first clip DMAD and continuations Turbo-8. S2 uses the recorded learned latent upscale and DMAD refinement at 1952×1088; the shared export uses S1 audio. See the graph values for exact scheduling and conditioning.

## Reproduction order

Render G1 S1, then G2/G3/G4 S1 using the preceding accepted state. Render G1 S2, then G2/G3/G4 S2 using each clip's S1 latent and the preceding S2 context where wired. Keep stages and resolutions distinct. The dependency map in [graph inventory](../graphs/inventory.json) identifies producers and unresolved inputs. Runtime latents are not model weights and are not included in this small package; regenerate them through the recorded predecessors. Replace `${COMFY_ROOT}` with your local backend root and stage the bound reference assets in ComfyUI input. Use a new output prefix throughout each rerun.

The archived graphs remain source evidence. `film.py` translates and executes their complete dependency chain with own inputs and guided approvals; see [guided filmmaking](../docs/GUIDED_FILM.md).

## What remains imperfect

Background people, clothing and baskets can change; the yellow-coated shopper partly resets, footsteps can outlast movement, and two prompts asked for an unnecessary backward step. The orbit is not a metrically verified camera path. Memory variants were separate experiments and are not silently added to this accepted main-chain recipe. This case is useful precisely because it shows both the method and its limits.

## Included reference files

Open a reference to download it at full resolution. Bindings identify the loader nodes; the prompts specify the picture roles.

[<img src="../assets/465f09b34f16d000.png" width="240" alt="Reference 465f09b34f16d000">](../assets/465f09b34f16d000.png)

Used by: `MARKET_G1_S1:sl1`, `MARKET_G1_S2:sl2`

[<img src="../assets/19f5d8d99bf8cd89.png" width="240" alt="Reference 19f5d8d99bf8cd89">](../assets/19f5d8d99bf8cd89.png)

Used by: `MARKET_G1_S1:ref0`, `MARKET_G1_S2:ref0`, `MARKET_G2_S1:ref0`, `MARKET_G2_S2:ref0`, `MARKET_G3_S1:ref0`, `MARKET_G3_S2:ref0`, `MARKET_G4_S1:ref0`, `MARKET_G4_S2:ref0`

[<img src="../assets/e7a3594f523322da.png" width="240" alt="Reference e7a3594f523322da">](../assets/e7a3594f523322da.png)

Used by: `MARKET_G1_S1:ref1`, `MARKET_G1_S2:ref1`, `MARKET_G2_S1:ref1`, `MARKET_G2_S2:ref1`, `MARKET_G3_S1:ref1`, `MARKET_G3_S2:ref1`, `MARKET_G4_S1:ref1`, `MARKET_G4_S2:ref1`

[<img src="../assets/782ed79bb020fa1b.png" width="240" alt="Reference 782ed79bb020fa1b">](../assets/782ed79bb020fa1b.png)

Used by: `MARKET_G1_S1:ref2`, `MARKET_G1_S2:ref2`, `MARKET_G2_S1:ref2`, `MARKET_G2_S2:ref2`, `MARKET_G3_S1:ref2`, `MARKET_G3_S2:ref2`, `MARKET_G4_S1:ref2`, `MARKET_G4_S2:ref2`

[<img src="../assets/04b6b1dccd9b71f6.png" width="240" alt="Reference 04b6b1dccd9b71f6">](../assets/04b6b1dccd9b71f6.png)

Used by: `MARKET_G1_S1:ref3`, `MARKET_G1_S2:ref3`, `MARKET_G2_S1:ref3`, `MARKET_G2_S2:ref3`, `MARKET_G3_S1:ref3`, `MARKET_G3_S2:ref3`, `MARKET_G4_S1:ref3`, `MARKET_G4_S2:ref3`

[<img src="../assets/1583209595066d64.png" width="240" alt="Reference 1583209595066d64">](../assets/1583209595066d64.png)

Used by: `MARKET_G1_S1:ref4`, `MARKET_G1_S2:ref4`, `MARKET_G2_S1:ref4`, `MARKET_G2_S2:ref4`, `MARKET_G3_S1:ref4`, `MARKET_G3_S2:ref4`, `MARKET_G4_S1:ref4`, `MARKET_G4_S2:ref4`

[<img src="../assets/678956be7ebca5ec.png" width="240" alt="Reference 678956be7ebca5ec">](../assets/678956be7ebca5ec.png)

Used by: `MARKET_G1_S1:ref5`, `MARKET_G1_S2:ref5`, `MARKET_G2_S1:ref5`, `MARKET_G2_S2:ref5`, `MARKET_G3_S1:ref5`, `MARKET_G3_S2:ref5`, `MARKET_G4_S1:ref5`, `MARKET_G4_S2:ref5`

[Audio input 7daef4885790a407.wav](../assets/7daef4885790a407.wav)

Used by: `MARKET_G2_S1:aud0`, `MARKET_G2_S2:aud0`

[Audio input ad7c4beffc59fecf.wav](../assets/ad7c4beffc59fecf.wav)

Used by: `MARKET_G2_S1:aud1`, `MARKET_G2_S2:aud1`

[<img src="../assets/c14f8a977daf0097.png" width="240" alt="Reference c14f8a977daf0097">](../assets/c14f8a977daf0097.png)

Used by: `MARKET_G3_S1:ref6`, `MARKET_G3_S2:ref6`, `MARKET_G4_S1:ref6`, `MARKET_G4_S2:ref6`

[<img src="../assets/556490c4374a1dbd.png" width="240" alt="Reference 556490c4374a1dbd">](../assets/556490c4374a1dbd.png)

Used by: `MARKET_G3_S1:ref7`, `MARKET_G3_S2:ref7`, `MARKET_G4_S1:ref7`, `MARKET_G4_S2:ref7`
