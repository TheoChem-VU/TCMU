import pathlib as pl
import sys

import git

current_dir = pl.Path(__file__).parent
sys.path.insert(0, str(current_dir.parent / "src" / "tcmu"))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "tcmu"
copyright = "2024, TheoCheM VU Amsterdam"
author = "TheoCheM VU Amsterdam"

# get release information
repo = git.Repo("..")

tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
if len(tags) == 0:
    latest_tag = None
    release = "vUnknown"
else:
    latest_tag = tags[-1]
    release = latest_tag.name

# print("Git data:")
# print("\tRepository:    ", repo)
# print("\tHeads:         ", repo.heads)
# print("\tTags:          ", tags)
# print("\tLatest Tag:    ", repr(latest_tag))
# print("\tLatest Version:", release)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_tabs.tabs",
    "sphinx_copybutton",
    # 'sphinx.ext.autosummary',
    "sphinx_autodoc_typehints",
    "sphinx_click",
]

napoleon_use_param = True
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


autodoc_default_options = {
    "autosummary": True,
}

modindex_common_prefix = ["tcmu"]

html_theme_options = {
    # "show_nav_level": 2,
    # "navigation_depth": 2,
    "navbar_end": ["star"],
    "navbar_center": [],
    "navbar_start": ["logo"],
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_favicon = "https://avatars.githubusercontent.com/u/119413491"
html_theme = "pydata_sphinx_theme"  # pip install pydata-sphinx-theme
html_static_path = ["_static"]
add_module_names = False
autodoc_member_order = "bysource"
html_sidebars = { '**': ['globaltoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html'] }
# custom variables
rst_epilog = f"""
.. |read| replace:: :func:`read <tcmu.results.read>`
.. |VDDmanager| replace:: :class:`VDDManager <tcmu.analysis.vdd.manager.VDDChargeManager>`
.. |VDDcharge| replace:: :class:`VDDCharge <tcmu.analysis.vdd.charge.VDDCharge>`
.. |change_unit| replace:: :func:`change_unit <tcmu.analysis.vdd.manager.VDDChargeManager.change_unit>`
.. |ProjectVersion| replace:: {release}
.. |cm-1| replace:: :math:`\\text{{cm}}^{{–1}}`
.. |kcal/mol| replace:: :math:`\\text{{kcal mol}}^{{–1}}`
.. |km/mol| replace:: :math:`\\text{{km mol}}^{{–1}}`
.. |angstrom| replace:: :math:`\\AA`
.. |Result| replace:: :class:`Result <tcmu.results.result.Result>`
.. |Job| replace:: :class:`Job <tcmu.job.generic.Job>`
.. |ADFJob| replace:: :class:`ADFJob <tcmu.job.adf.ADFJob>`
.. |ADFFragmentJob| replace:: :class:`ADFFragmentJob <tcmu.job.adf.ADFFragmentJob>`
.. |DFTBJob| replace:: :class:`DFTBJob <tcmu.job.dftb.DFTBJob>`
.. |NMRJob| replace:: :class:`NMRJob <tcmu.job.nmr.NMRJob>`
.. |ORCAJob| replace:: :class:`ORCAJob <tcmu.job.orca.ORCAJob>`
.. |CRESTJob| replace:: :class:`CRESTJob <tcmu.job.crest.CRESTJob>`
.. |QCGJob| replace:: :class:`QCGJob <tcmu.job.crest.QCGJob>`
.. |XTBJob| replace:: :class:`XTBJob <tcmu.job.xtb.XTBJob>`
"""
