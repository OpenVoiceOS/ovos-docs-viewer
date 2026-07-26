import shutil
import zipfile
from pathlib import Path
from typing import Iterable, Dict

import click
import requests
from ovos_utils.xdg_utils import xdg_data_home
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import DirectoryTree, Footer, Header, MarkdownViewer

# URLs for documentation resources
DOCS_URLS = {
    "live-status": "https://github.com/OpenVoiceOS/status/raw/refs/heads/master/README.md",
    "raspOVOS": "https://github.com/TigreGotico/raspOVOS/raw/refs/heads/master/README.md",
    "installer": "https://github.com/OpenVoiceOS/ovos-installer/raw/refs/heads/main/README.md",
    "technical": "https://github.com/OpenVoiceOS/ovos-technical-manual/archive/refs/heads/master.zip",
    "messages": "https://github.com/OpenVoiceOS/message_spec/archive/refs/heads/master.zip",
    "hivemind": "https://github.com/JarbasHiveMind/HiveMind-community-docs/archive/refs/heads/master.zip",
}

SKILLS = ['https://github.com/OpenVoiceOS/ovos-skill-alerts',
          'https://github.com/OpenVoiceOS/ovos-skill-application-launcher',
          'https://github.com/OpenVoiceOS/ovos-skill-audio-recording',
          'https://github.com/OpenVoiceOS/ovos-skill-bandcamp',
          'https://github.com/OpenVoiceOS/ovos-skill-boot-finished',
          'https://github.com/OpenVoiceOS/ovos-skill-camera',
          'https://github.com/OpenVoiceOS/ovos-skill-cmd',
          'https://github.com/OpenVoiceOS/ovos-skill-color-picker',
          'https://github.com/OpenVoiceOS/ovos-skill-confucius-quotes',
          'https://github.com/OpenVoiceOS/ovos-skill-date-time',
          'https://github.com/OpenVoiceOS/ovos-skill-days-in-history',
          'https://github.com/OpenVoiceOS/ovos-skill-ddg',
          'https://github.com/OpenVoiceOS/ovos-skill-dictation',
          'https://github.com/OpenVoiceOS/ovos-skill-easter-eggs',
          'https://github.com/OpenVoiceOS/ovos-skill-fallback-chatgpt',
          'https://github.com/OpenVoiceOS/ovos-skill-fallback-unknown',
          'https://github.com/OpenVoiceOS/ovos-skill-ggwave',
          'https://github.com/OpenVoiceOS/ovos-skill-hello-world',
          'https://github.com/OpenVoiceOS/ovos-skill-homescreen',
          'https://github.com/OpenVoiceOS/ovos-skill-icanhazdadjokes',
          'https://github.com/OpenVoiceOS/ovos-skill-ip',
          'https://github.com/OpenVoiceOS/ovos-skill-iss-location',
          'https://github.com/OpenVoiceOS/ovos-skill-laugh',
          'https://github.com/OpenVoiceOS/ovos-skill-local-media',
          'https://github.com/OpenVoiceOS/ovos-skill-moviemaster',
          'https://github.com/OpenVoiceOS/ovos-skill-naptime',
          'https://github.com/OpenVoiceOS/ovos-skill-news',
          'https://github.com/OpenVoiceOS/ovos-skill-number-facts',
          'https://github.com/OpenVoiceOS/ovos-skill-parrot',
          'https://github.com/OpenVoiceOS/ovos-skill-personal',
          'https://github.com/OpenVoiceOS/ovos-skill-pyradios',
          'https://github.com/OpenVoiceOS/ovos-skill-randomness',
          'https://github.com/OpenVoiceOS/ovos-skill-screenshot',
          'https://github.com/OpenVoiceOS/ovos-skill-somafm',
          'https://github.com/OpenVoiceOS/ovos-skill-soundcloud',
          'https://github.com/OpenVoiceOS/ovos-skill-speedtest',
          'https://github.com/OpenVoiceOS/ovos-skill-spelling',
          'https://github.com/OpenVoiceOS/ovos-skill-spotify',
          'https://github.com/OpenVoiceOS/ovos-skill-tunein',
          'https://github.com/OpenVoiceOS/ovos-skill-volume',
          'https://github.com/OpenVoiceOS/ovos-skill-wallpapers',
          'https://github.com/OpenVoiceOS/ovos-skill-weather',
          'https://github.com/OpenVoiceOS/ovos-skill-wikihow',
          'https://github.com/OpenVoiceOS/ovos-skill-wikipedia',
          'https://github.com/OpenVoiceOS/ovos-skill-wolfie',
          'https://github.com/OpenVoiceOS/ovos-skill-word-of-the-day',
          'https://github.com/OpenVoiceOS/ovos-skill-wordnet',
          'https://github.com/OpenVoiceOS/ovos-skill-youtube',
          'https://github.com/OpenVoiceOS/ovos-skill-youtube-music']
SKILLS = [f"{s}/raw/refs/heads/dev/README.md" for s in SKILLS]


def download_skills(force: bool = False) -> str:

    base_path = Path(xdg_data_home()) / "ovos_docs" / "skills" / "docs"
    base_path.mkdir(parents=True, exist_ok=True)

    for url in SKILLS:
        print(f"downloading: {url}")
        key = url.split("https://github.com/OpenVoiceOS/")[-1].split("/")[0]

        skill_doc = base_path / f"{key}.md"
        # Skip download if folder exists and not forcing a re-download
        if not force and skill_doc.exists():
            continue

        response = requests.get(url)
        response.raise_for_status()

        with open(skill_doc, "w") as f:
            f.write(response.text)

    return str(base_path)


def download_docs(force: bool = False) -> Dict[str, str]:
    """
    Downloads and prepares documentation from URLs.

    Args:
        force (bool): Whether to force re-download of existing documentation.

    Returns:
        Dict[str, str]: A mapping of documentation keys to their local paths.
    """
    base_path = Path(xdg_data_home()) / "ovos_docs"
    base_path.mkdir(parents=True, exist_ok=True)
    docs_paths = {}

    for key, url in DOCS_URLS.items():
        doc_folder = base_path / key

        # Skip if folder exists and not forcing a re-download
        if not (force or key == "live-status") and doc_folder.exists():
            docs_paths[key] = str(doc_folder / "docs")
            continue

        print(f"downloading: {url}")
        response = requests.get(url)
        response.raise_for_status()

        if url.endswith(".zip"):
            zip_path = doc_folder.with_suffix(".zip")
            with open(zip_path, "wb") as f:
                f.write(response.content)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # GitHub branch archives extract to "<repo>-<branch>", not "<branch>-<branch>"
                repo_name = url.split("/archive/")[0].split("/")[-1]
                branch = url.split("/")[-1].replace(".zip", "")
                extracted_name = f"{repo_name}-{branch}"
                zip_ref.extractall(base_path)
                shutil.move(base_path / extracted_name, doc_folder)
            zip_path.unlink()
        else:
            doc_folder.mkdir(parents=True, exist_ok=True)
            (doc_folder / "docs").mkdir(exist_ok=True)
            with open(doc_folder / "docs" / f"{key}.md", "w") as f:
                f.write(response.text)

        docs_paths[key] = str(doc_folder / "docs")

    docs_paths["skills"] = download_skills(force)
    return docs_paths


class FilteredDirectoryTree(DirectoryTree):
    """Directory tree widget with filters to show only relevant files."""

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if not path.name.startswith(".") and path.name.endswith(".md")]


class Documentation(App):
    """Textual markdown browser app for viewing documentation."""

    BINDINGS = [("q", "quit", "Quit")]
    docs_paths: Dict[str, str] = {}

    def __init__(self, selected_doc: str, *args, **kwargs):
        """
        Initialize the application.

        Args:
            selected_doc (str): The key of the selected documentation to view.
        """
        self.selected_doc = selected_doc
        if not self.docs_paths:
            self.docs_paths = download_docs()
        super().__init__(*args, **kwargs)

    @property
    def markdown_viewer(self) -> MarkdownViewer:
        """Get the MarkdownViewer widget."""
        viewer = self.query_one(MarkdownViewer)
        viewer.show_table_of_contents = False
        return viewer

    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        docs_path = self.docs_paths.get(self.selected_doc)
        if not docs_path:
            raise ValueError(f"Documentation '{self.selected_doc}' not found.")

        yield Header()
        with Horizontal():
            directory_tree = FilteredDirectoryTree(docs_path, id="tree-view")
            directory_tree.styles.width = "20%"
            yield directory_tree
            with VerticalScroll(id="code-view"):
                yield MarkdownViewer(id="code")
        yield Footer()

    def on_mount(self) -> None:
        """Called after the app mounts."""
        self.query_one(DirectoryTree).focus()

    async def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """
        Handle file selection in the directory tree.

        Args:
            event (DirectoryTree.FileSelected): The event triggered on file selection.
        """
        try:
            await self.markdown_viewer.go(str(event.path))
            self.markdown_viewer.scroll_home(animate=False)
        except FileNotFoundError:
            self.exit(message=f"Unable to load file: {event.path}")
        except Exception as e:
            self.sub_title = f"ERROR: {e}"


@click.command(help=f"View documentation for: {' | '.join(['skills'] + list(DOCS_URLS.keys()))}")
@click.argument('docs')
def launch(docs: str):
    f"""Launch the documentation viewer."""
    assert docs in ['skills'] + list(DOCS_URLS.keys())
    Documentation(selected_doc=docs).run()


if __name__ == "__main__":
    launch()
