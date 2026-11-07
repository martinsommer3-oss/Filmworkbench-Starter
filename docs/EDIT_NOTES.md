# Editing notes — separate from the v0.1 film runner

These are observations from our development films. The specialized edit tools and their installations are not included in this release.

Useful in tested cases:

- **Trim or remove a section:** cut before a repeated action, shorten an ending, or place a state change across an intentional cut. An ellipse did not convincingly repair every hand/object action we tried.
- **Crop and reframe:** isolate the useful part of an existing shot. This preserves the original performance, lip movements and voice, at the cost of framing and resolution.
- **Repair audio locally:** replace an unwanted sound with nearby room tone, adjust a loud word and use short fades. CPU denoising with DeepFilterNet helped in tested noise cases; it can also soften useful sounds.
- **Replace a short shot:** use a frame from the finished film plus character references to generate a replacement, then insert it at exact frame boundaries. Match the color and the state expected by the following shot. A newly generated speaking shot may change the voice and timing.
- **H3 video-conditioned editing:** feeding an existing short shot as a video reference and describing a changed action worked in a tested object-handling case. It is not a general guarantee of precise edits.
- **Masked edits:** experimental local repairs worked in some cases, with moving foreground masks needed when people crossed the edited region.

Still open: reliable arbitrary object replacement, identity repair, changing a speaking shot while preserving the original voice/lip sync, and edits at a continuation seam without invalidating later clips. Additional lip-sync and audio-separation approaches were considered but are not validated here.

The included film runner already supports rejecting and rerendering a stage. It conservatively invalidates all later work; this is different from repairing a small region of a finished movie. A future chat-directed editor could select among the approaches above, but v0.1 does not promise commands such as "replace this person at second 12".
