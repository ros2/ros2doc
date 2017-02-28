import sys
import os

extensions = ['breathe', 'sphinx.ext.viewcode', 'sphinx.ext.autodoc']
breathe_projects = { '{{ pkg_name }}': '{{doxygen_path}}' }
breathe_default_project = '{{ pkg_name }}'
breathe_domain_by_extension = { "h": "cpp" }
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = '{{ pkg_name }}'
copyright = u'2017'
author = u'ros2'
version = u'0.0.1'
release = u'0.0.1'
language = None
exclude_patterns = ['_build']
pygments_style = 'sphinx'
todo_include_tools = False
html_theme = 'classic'
html_theme_options = { 'rightsidebar': True }
html_static_path = ['_static']
htmlhelp_basename = '{{ pkg_name }}'
latex_elements = { }
latex_documents = [ (master_doc, '{{ pkg_name }}.tex', u'{{ pkg_name }} Documentation', u'ros', 'manual') ]
man_pages = [ (master_doc, '{{ pkg_name }}', u'{{ pkg_name }} Documentation', [author], 1) ]
texinfo_documents = [ (master_doc, '{{ pkg_name }}', u'{{ pkg_name }} Documentation', author, '{{ pkg_name }}', 'description', 'Miscellaneous') ]

