# ovos-docs-viewer

A terminal application that shows OpenVoiceOS documentation. It downloads the docs from GitHub and displays them in a text-based browser. A file tree sits on the left, and a markdown viewer sits on the right.

![docs](https://github.com/JarbasHiveMind/HiveMind-community-docs/assets/33701864/3f241128-3dd3-47ef-857c-722e560328e9)

## Installation

```bash
pip install ovos-docs-viewer
```

## Usage

```bash
$ ovos-docs-viewer --help
Usage: ovos-docs-viewer [OPTIONS] {skills|live-status|raspOVOS|installer|technical|messages|hivemind|architecture}

  View documentation for one of:

  skills       skill READMEs
  technical    the OVOS technical manual
  messages     the bus message spec
  hivemind     HiveMind community docs
  architecture the OVOS formal specifications (protocol/ABI specs)
  live-status  live ecosystem status, always re-fetched
  raspOVOS     raspOVOS user docs
  installer    ovos-installer docs

  Files are cached under $XDG_DATA_HOME/ovos_docs (default
  ~/.local/share/ovos_docs). Use --refresh to wipe and re-download.

Options:
  --refresh  Wipe and re-download the cached documentation before launching.
  --help     Show this message and exit.
```

Pick a documentation set from the list above. The tool downloads the matching docs on first use and caches them locally under `$XDG_DATA_HOME/ovos_docs` (`~/.local/share/ovos_docs` by default). Use the file tree to pick a page, and read it in the markdown viewer.

Pass `--refresh` to wipe the cache and re-download before launching. Note that `live-status` is always re-fetched on every run, refresh or not, since it tracks live ecosystem state rather than a stable doc set.

![1](https://github.com/user-attachments/assets/53f52149-e775-4f31-aafb-d344c339cd17)

![2](https://github.com/user-attachments/assets/bfa37d5d-bb41-4c00-b81f-ca6b112c0b60)

![3](https://github.com/user-attachments/assets/5354d95f-744b-4886-b830-46f8b388b017)

## Related projects

- [OpenVoiceOS/ovos-technical-manual](https://github.com/OpenVoiceOS/ovos-technical-manual): the technical manual shown by the `technical` doc set.
- [OpenVoiceOS/ovos-installer](https://github.com/OpenVoiceOS/ovos-installer): the installer shown by the `installer` doc set.
- [OpenVoiceOS/message_spec](https://github.com/OpenVoiceOS/message_spec): the bus message spec shown by the `messages` doc set.
- [OpenVoiceOS/status](https://github.com/OpenVoiceOS/status): the status page shown by the `live-status` doc set.
- [TigreGotico/raspOVOS](https://github.com/TigreGotico/raspOVOS): the raspOVOS docs shown by the `raspOVOS` doc set.
- [JarbasHiveMind/HiveMind-community-docs](https://github.com/JarbasHiveMind/HiveMind-community-docs): the HiveMind docs shown by the `hivemind` doc set.
- [OpenVoiceOS/architecture](https://github.com/OpenVoiceOS/architecture): the formal OVOS specifications shown by the `architecture` doc set.

## License

See the [LICENSE](LICENSE) file.
