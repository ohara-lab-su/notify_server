import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
project = "notify-frame"
from importlib.metadata import PackageNotFoundError, version as package_version
try:
    release = package_version("notify-frame")
except PackageNotFoundError:
    release = "unknown"
version = release
language = os.environ.get("DOC_LANGUAGE", "en")
root_doc = "index"
source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
extensions = ["myst_parser", "sphinx.ext.autodoc", "sphinx.ext.autosummary", "sphinx.ext.napoleon", "sphinx.ext.viewcode"]
autosummary_generate = True
autodoc_default_options = {"members": True, "undoc-members": True, "show-inheritance": True}
html_theme = "sphinx_rtd_theme"
html_theme_options = {"collapse_navigation": False, "navigation_depth": 4, "titles_only": False}
exclude_patterns = ["_build"]
