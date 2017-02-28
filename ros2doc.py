#!/usr/bin/env python3
import ament_package
import ament_tools.verbs.list_packages
from ament_tools.package_types import parse_package
import datetime
import errno
import os
import shutil
import subprocess
import sys

def run_shell_command(cmd, in_path=None):
    print("running command in path [%s]: %s" % (in_path, cmd))
    subprocess.call(cmd, shell=True, cwd=in_path)

def make_index_file(path, pkg_paths, basepath):
    pkgs = [ ]
    for pkg_path in pkg_paths:
        pkg_abspath = os.path.join(basepath, pkg_path)
        pkg = parse_package(pkg_abspath)
        pkgs.append(pkg.name)
    index_file = open(path, 'w')
    index_file.write("""<html>
  <head>
    <title>ROS 2 package index</title>
  </head>
  <body>
    <h1>ROS 2 packages</h1>
    <ul>
""")
    pkgs.sort()
    for name in pkgs:
        pkg_doc_path = os.path.join(os.path.dirname(path), name)
        if os.path.exists(pkg_doc_path):
            print("found")
            index_file.write("<li><a href='{0}/index.html'>{0}</a></li>\n".format(name))
        else:
            index_file.write("<li>{0}</li>\n".format(name))

    index_file.write("""
    </ul>
  </body>
</html>
""")
    index_file.close()

def update_symlink(target, link_name):
    # http://stackoverflow.com/questions/8299386/modifying-a-symlink-in-python
    try:
        os.symlink(target, link_name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(link_name)
            os.symlink(target, link_name)
        else:
            raise e

def awesome():
    if len(sys.argv) < 2:
        print("usage: ros2doc SOURCEPATH")
        sys.exit(1)

    dt = datetime.datetime.now()

    buildpath = os.path.abspath(os.path.join('docbuild', dt.strftime('%Y%m%d.%H%M%S')))
    os.makedirs(buildpath)
    update_symlink(buildpath, os.path.join('docbuild', 'latest'))
    
    pkgs_doc_path = os.path.join(buildpath, 'pkgs')
    os.makedirs(pkgs_doc_path)
    
    html_output_path = os.path.abspath(os.path.join(buildpath, 'html'))
    os.makedirs(html_output_path)
   
    basepath = sys.argv[1]
    print("running on sourcepath {0}".format(basepath))
    pkg_paths = ament_tools.verbs.list_packages.find_package_paths(basepath)

    for pkg_path in pkg_paths:
        pkg_abspath = os.path.join(basepath, pkg_path)
        pkg = parse_package(pkg_abspath)
        #if pkg.name != 'joy':
        #    continue
        pkg_copy_path = os.path.join(pkgs_doc_path, pkg.name)
        if os.path.exists(pkg_copy_path):
            continue
        shutil.copytree(pkg_abspath, pkg_copy_path)
        doc_path = os.path.join(pkg_copy_path, 'doc')
        if os.path.exists(doc_path):
            pkg_html_output_path = os.path.join(html_output_path, pkg.name)
            os.makedirs(pkg_html_output_path)
            # hooray there is a doc directory. let's create a conf.py in there
            conf_py_path = os.path.join(doc_path, 'conf.py')
            print("hai i will now create a conf.py at %s" % conf_py_path)
            if not os.path.isfile(conf_py_path):
                with open(conf_py_path, 'w') as f:
                    f.write("""\
import sys
import os
extensions = []
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'{0}'
copyright = u'2017'
author = u'ros'
version = u'0.0.1'
release = u'0.0.1'
language = None
exclude_patterns = ['_build']
pygments_style = 'sphinx'
todo_include_tools = False
html_theme = 'alabaster'
html_static_path = ['_static']
htmlhelp_basename = '{0}'
latex_elements = {{ }}
latex_documents = [ (master_doc, '{0}.tex', u'{0} Documentation', u'ros', 'manual') ]
man_pages = [ (master_doc, '{0}', u'{0} Documentation', [author], 1) ]
texinfo_documents = [ (master_doc, '{0}', u'{0} Documentation', author, '{0}', 'description', 'Miscellaneous') ]
""".format(pkg.name))
    run_shell_command("sphinx-build -b html . {0}".format(pkg_html_output_path), doc_path)
    make_index_file(os.path.join(html_output_path, 'index.html'), pkg_paths, basepath)

if __name__ == '__main__':
    awesome()
