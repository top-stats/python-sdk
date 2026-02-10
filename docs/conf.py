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
  'light_logo': 'banner-light-mode.svg',
  'dark_logo': 'banner-dark-mode.svg',
  'sidebar_hide_name': True,
  'top_of_page_buttons': ['edit'],
  'footer_icons': [
    {
      'name': 'GitHub',
      'url': 'https://github.com/top-stats/python-sdk',
      'html': """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
      'class': '',
    },
  ],
}
html_theme = 'furo'
html_title = project
html_favicon = '_static/favicon.ico'
