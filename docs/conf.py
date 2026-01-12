import sys
import os
import re


sys.path.insert(0, os.path.join(os.getcwd(), '..', 'topstats'))
sys.path.insert(0, os.path.abspath('..'))

from version import VERSION


project = 'topstats'
author = 'null8626'

copyright = ''
with open('../LICENSE', 'r') as f:
  copyright = re.search(r'[\d\-]+ null8626', f.read()).group()

version = VERSION
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx', 'sphinx_reredirects']

intersphinx_mapping = {
  'py': ('https://docs.python.org/3', None),
  'aio': ('https://docs.aiohttp.org/en/stable/', None),
}

redirects = {
  'support-server': 'https://discord.com/invite/jjEauJXuZc',
  'repository': 'https://github.com/top-stats/python-sdk',
  'raw-api-reference': 'https://docs.topstats.gg/docs/',
}

html_css_files = [
  'style.css',
  'https://fonts.googleapis.com/css2?family=Inter:wght@100..900&family=Roboto+Mono&display=swap',
]
html_js_files = ['script.js']
html_static_path = ['_static']
html_theme_options = {
    "light_logo": "banner-light-mode.svg",
    "dark_logo": "banner-dark-mode.svg",
    "sidebar_hide_name": True,
    "top_of_page_buttons": ["edit"],
}
html_theme = 'furo'
html_title = project
html_favicon = '_static/favicon.ico'
