# Public releases and private development

The public project is [Filmworkbench-Starter](https://github.com/martinsommer3-oss/Filmworkbench-Starter); the first release is [v0.1.0](https://github.com/martinsommer3-oss/Filmworkbench-Starter/releases/tag/v0.1.0). The private production repository remains separate and private. This public repository starts with its own source snapshot, not the private Git history.

## Downloads and browsing

- [Starter ZIP](https://github.com/martinsommer3-oss/Filmworkbench-Starter/releases/download/v0.1.0/Filmworkbench-v0.1-starter.zip): code, documentation, original recipe graphs, full-resolution reference inputs and workflow overviews.
- [Examples ZIP](https://github.com/martinsommer3-oss/Filmworkbench-Starter/releases/download/v0.1.0/Filmworkbench-v0.1-examples.zip): ten selected S2 videos. Extract at the starter root; each video lands in `examples/<case>/video_S2.mp4` beside its overview.
- [Example gallery](../examples/README.md): direct MP4 links plus per-scene overview and render-data navigation. Release videos are downloadable files; inline streaming in GitHub Markdown is not promised.

`examples/catalog.json` binds each local video path to a unique `release_asset` filename, public URL and SHA-256. Videos are release assets, not Git history. GitHub's [release documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases) permits assets smaller than 2 GiB each.

## Updating the public version

Select the improved code/recipes/assets, update this public tree, run its checks, review the exported files, and publish a new version. Keep previous release assets and tags available. Private edits are not synchronized automatically. Contributors can propose changes against this public repository.

The per-case `render-data/` files are generated copies of canonical `graphs/` and `recipes/` records. Their manifests record the source hashes; keep both copies synchronized when preparing a release. Shared full-resolution images/audio live in `assets/` to avoid duplicating large inputs across cases.

Never publish private chat logs, provider credentials, personal license documents, model weights or third-party custom-node implementations as part of this source export. Link dependencies to their original publishers.
