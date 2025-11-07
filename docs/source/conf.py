# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))  # Add src to path

# -- Project information -----------------------------------------------------

project = 'Rocket Simulation Framework'
copyright = '2025, STARPI Team'
author = 'STARPI Team'

# The full version, including alpha/beta/rc tags
release = '1.0.0'
version = '1.0'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',  # Auto-generate documentation from docstrings
    'sphinx.ext.autosummary',  # Create summary tables
    'sphinx.ext.napoleon',  # Support for NumPy and Google style docstrings
    'sphinx.ext.viewcode',  # Add links to highlighted source code
    'sphinx.ext.intersphinx',  # Link to other project's documentation
    'sphinx.ext.mathjax',  # Render math via MathJax
    'sphinx.ext.todo',  # Support for todo items
    'sphinx.ext.coverage',  # Check documentation coverage
    'sphinx_design',  # Grid layouts and cards
    'myst_parser',  # Markdown support
    'nbsphinx',  # Jupyter notebook support
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'pydata_sphinx_theme'  # NumPy/SciPy style theme

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "github_url": "https://github.com/starpi/rocket-sim",  # Update with actual URL
    "collapse_navigation": False,
    "navigation_depth": 4,
    "show_prev_next": True,
    "navbar_end": ["navbar-icon-links", "search-field"],
    "footer_items": ["copyright"],
    "logo": {
        "text": "Rocket Sim",
        "image_dark": "_static/logo_dark.png",  # Optional
        "image_light": "_static/logo_light.png",  # Optional
    },
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# -- Options for autodoc -----------------------------------------------------

# Automatically extract typehints when specified and place them in
# descriptions of the relevant function/method.
autodoc_typehints = 'description'

# Don't show class signature with the class' name.
autodoc_class_signature = "separated"

# -- Options for autosummary -------------------------------------------------

autosummary_generate = True  # Turn on sphinx.ext.autosummary
autoclass_content = "both"  # Add __init__ doc (if exists) to class summary

# -- Options for napoleon (NumPy/Google style docstrings) -------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Options for intersphinx -------------------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
}

# -- Options for nbsphinx ----------------------------------------------------

# Execute notebooks before conversion: 'always', 'never', 'auto' (default)
nbsphinx_execute = 'never'  # Don't execute notebooks during build

# -- Options for MathJax -----------------------------------------------------

mathjax_path = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"

# -- Options for MyST --------------------------------------------------------

# Enable MyST extensions
myst_enable_extensions = [
    "colon_fence",  # ::: instead of ``` for directives
    "deflist",  # Definition lists
    "dollarmath",  # $...$ and $$...$$ for math
    "fieldlist",  # Field lists
    "html_admonition",  # HTML admonitions
    "html_image",  # HTML images
    "linkify",  # Auto-detect URLs
    "replacements",  # Text replacements
    "smartquotes",  # Smart quotes
    "substitution",  # Variable substitutions
    "tasklist",  # Task lists
]

# -- Custom CSS --------------------------------------------------------------

def setup(app):
    app.add_css_file('custom.css')
