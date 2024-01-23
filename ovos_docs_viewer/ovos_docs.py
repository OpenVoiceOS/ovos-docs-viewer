import os
import os.path
import shutil
import zipfile
from pathlib import Path
from typing import Iterable

import click
import requests
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import DirectoryTree, Footer, Header, MarkdownViewer
from ovos_utils.xdg_utils import xdg_data_home

_urls = {
    "hivemind": "https://github.com/JarbasHiveMind/HiveMind-community-docs/archive/refs/heads/master.zip",
    "community": "https://github.com/OpenVoiceOS/community-docs/archive/refs/heads/master.zip",
    "technical": "https://github.com/OpenVoiceOS/ovos-technical-manual/archive/refs/heads/master.zip",
    "messages": "https://github.com/OpenVoiceOS/message_spec/archive/refs/heads/master.zip",
}


def download(force=False):
    p = f"{xdg_data_home()}/ovos_docs"
    os.makedirs(p, exist_ok=True)
    for k, url in _urls.items():
        folder = f"{p}/{k}"
        if not force and os.path.isdir(folder):
            continue
        data = requests.get(url, timeout=30).content
        zi = folder + ".zip"
        with open(zi, "wb") as file:
            file.write(data)

        items = url.split("/")

        with zipfile.ZipFile(zi, "r") as zip_ref:
            zip_ref.extractall(p)
            if os.path.exists(f"{p}/{k}"):
                shutil.rmtree(f"{p}/{k}")
            shutil.move(f"{p}/{items[4]}-master", f"{p}/{k}")
        Documentation.docs[k] = f"{folder}/docs"
    return Documentation.docs


class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [
            path
            for path in paths
            if not path.name.startswith(".") and path.name.endswith(".md")
        ]


class Documentation(App):
    """Textual markdown browser app."""

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]
    DOCSK = "technical"
    docs = {k: f"{xdg_data_home()}/ovos_docs/{k}/docs" for k in _urls.keys()}

    def __init__(self, *args, **kwargs):
        download()
        super().__init__(*args, **kwargs)

    @property
    def markdown_viewer(self) -> MarkdownViewer:
        """Get the Markdown widget."""
        m = self.query_one(MarkdownViewer)
        m.show_table_of_contents = False
        return m

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        path = self.docs[self.DOCSK]
        yield Header()
        with Horizontal():
            t = FilteredDirectoryTree(path, id="tree-view")
            t.styles.width = "20%"
            yield t
            with VerticalScroll(id="code-view"):
                yield MarkdownViewer(id="code")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(DirectoryTree).focus()

    async def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Called when the user click a file in the directory tree."""
        event.stop()
        try:
            self.query_one(DirectoryTree).focus()
            try:
                await self.markdown_viewer.go(str(event.path))
                self.markdown_viewer.scroll_home(animate=False)
            except FileNotFoundError:
                self.exit(message=f"Unable to load {self.path!r}")
        except Exception:
            self.sub_title = "ERROR"
        else:
            self.sub_title = str(event.path)


@click.command(
    help="Launch docs viewer, choose one of 'community', 'technical', 'hivemind', 'messages'"
)
@click.argument("docs")
def launch(docs):
    assert docs in ["hivemind", "community", "technical", "messages"]
    Documentation.DOCSK = docs
    Documentation().run()


if __name__ == "__main__":
    launch()
