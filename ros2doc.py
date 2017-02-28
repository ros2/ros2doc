#!/usr/bin/env python3
import ament_package
import ament_tools.verbs.list_packages
from ament_tools.package_types import parse_package
import datetime
import errno
import jinja2
import os
import shutil
import subprocess
import sys

def run_shell_command(cmd, in_path=None):
    print("running command in path [%s]: %s" % (in_path, cmd))
    subprocess.call(cmd, shell=True, cwd=in_path)

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

def jinja_autoescape(template_name):
    if template_name is None:
        return False
    if template_name.endswith(('.html')):
        return True

def awesome():
    ros2doc_path = os.path.abspath('.')  # yeah that's probably not great
    jinja_env = jinja2.Environment(loader=jinja2.PackageLoader('ros2doc', 'templates'), autoescape=jinja_autoescape)

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
    pkg_names = [ ]

    for pkg_path in pkg_paths:
        pkg_abspath = os.path.join(basepath, pkg_path)
        pkg = parse_package(pkg_abspath)
        pkg_names.append([pkg.name, False])
        #if pkg.name != 'joy':
        #    continue
        pkg_copy_path = os.path.join(pkgs_doc_path, pkg.name)
        if os.path.exists(pkg_copy_path):
            print("copy path exists")
            continue
        shutil.copytree(pkg_abspath, pkg_copy_path)
        doc_path = os.path.join(pkg_copy_path, 'doc')
        print("looking in %s" % doc_path)
        if not os.path.exists(doc_path):
            os.makedirs(doc_path)
        if True:
            print("doc path exists")
            pkg_html_output_path = os.path.join(html_output_path, pkg.name)
            os.makedirs(pkg_html_output_path)
            # hooray there is a doc directory. let's create a conf.py in there
            doxygen_conf_path = os.path.join(doc_path, 'doxygen.conf')
            doxygen_conf_template = jinja_env.get_template('doxygen.conf')
            doxygen_conf_file = open(doxygen_conf_path, 'w')
            doxygen_conf_file.write(doxygen_conf_template.render(pkg_name=pkg.name))
            doxygen_conf_file.close()
            run_shell_command("doxygen doxygen.conf", doc_path)

            doxygen_path = os.path.join(doc_path, 'doxygen', 'xml')

            sphinx_index_filename = os.path.join(doc_path, 'index.rst')
            if not os.path.exists(sphinx_index_filename):
                print("creating sphinx index file at {0}".format(sphinx_index_filename))
                sphinx_index_template = jinja_env.get_template('index.rst')
                sphinx_index_file = open(sphinx_index_filename, 'w')
                sphinx_index_file.write(sphinx_index_template.render(pkg_name=pkg.name))
                sphinx_index_file.close()

            conf_py_path = os.path.join(doc_path, 'conf.py')
            print("hai i will now create a conf.py at %s" % conf_py_path)
            conf_py_file = open(conf_py_path, 'w')
            conf_py_template = jinja_env.get_template('conf.py')
            conf_py_file.write(conf_py_template.render(pkg_name=pkg.name, doxygen_path=doxygen_path))
            conf_py_file.close()
            #run_shell_command("sphinx-build -b html . {0}".format(pkg_html_output_path), doc_path)
            run_shell_command("{0}/sphinx3-build -b html . {1}".format(ros2doc_path, pkg_html_output_path), doc_path)
            pkg_names[-1][1] = True  # we've built docs for this pkg

    pkg_names.sort()
    # make the index file
    index_template = jinja_env.get_template('index.html')
    index_file_name = os.path.join(html_output_path, 'index.html')
    print("creating index file at {0}".format(index_file_name))
    index_file = open(index_file_name, 'w')
    index_file.write(index_template.render(pkg_names=pkg_names))
    index_file.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: ros2doc SOURCEPATH")
        sys.exit(1)
    awesome()
