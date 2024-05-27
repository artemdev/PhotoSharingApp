import sys
import os
project = 'PhotoSharingApp'
copyright = '2024, Valeriy Yaremenko'
author = 'Valeriy Yaremenko'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


extensions = ['sphinx.ext.autodoc']

html_theme = 'nature'
html_static_path = ['_static']
