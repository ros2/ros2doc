#!/usr/bin/env python3
import ament_package
import ament_tools.verbs.list_packages
from ament_tools.package_types import parse_package
import argparse
import datetime
import errno
import jinja2
import os
import shutil
import subprocess
import sys

ACTUALLY_RUN_DOCGEN = True

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

def parse_pkgs():
    basepath = sys.argv[1]
    print("running on sourcepath {0}".format(basepath))
    pkg_paths = ament_tools.verbs.list_packages.find_package_paths(basepath)
    pkgs = [ ]
    for pkg_path in pkg_paths:
        pkg_dict = { }
        pkg_dict['abspath'] = os.path.join(basepath, pkg_path)
        pkg_dict['parsed'] = parse_package(pkg_dict['abspath'])
        pkg_dict['name'] = pkg_dict['parsed'].name
        pkg_dict['generated'] = False
        pkgs.append(pkg_dict)
    return pkgs

def generate_pkg_doc(pkgs_doc_path, pkgs_html_root, pkg, jinja_env):
    # first, we need to copy the sources somewhere temporary because we'll
    # probably generate debris that we don't want to clutter up the source tree
    pkg_copy_path = os.path.join(pkgs_doc_path, pkg['name'])
    if os.path.exists(pkg_copy_path):
        print("copy path exists")
        return

    shutil.copytree(pkg['abspath'], pkg_copy_path)
    doc_path = os.path.join(pkg_copy_path, 'doc')
    print("looking in %s" % doc_path)
    if not os.path.exists(doc_path):
        os.makedirs(doc_path)

    print("doc path exists")
    pkg_html_output_path = os.path.join(pkgs_html_root, pkg['name'])
    os.makedirs(pkg_html_output_path)
    # hooray there is a doc directory. let's create a conf.py in there
    doxygen_conf_path = os.path.join(doc_path, 'doxygen.conf')
    doxygen_conf_template = jinja_env.get_template('doxygen.conf')
    doxygen_conf_file = open(doxygen_conf_path, 'w')
    doxygen_conf_file.write(doxygen_conf_template.render(pkg_name=pkg['name']))
    doxygen_conf_file.close()
    if ACTUALLY_RUN_DOCGEN:
        run_shell_command("doxygen doxygen.conf", doc_path)

    doxygen_path = os.path.join(doc_path, 'doxygen', 'xml')

    sphinx_index_filename = os.path.join(doc_path, 'index.rst')
    if not os.path.exists(sphinx_index_filename):
        print("creating sphinx index file at {0}".format(sphinx_index_filename))
        sphinx_index_template = jinja_env.get_template('index.rst')
        sphinx_index = open(sphinx_index_filename, 'w')
        sphinx_index.write(sphinx_index_template.render(pkg_name=pkg['name']))
        sphinx_index.close()

    conf_py_path = os.path.join(doc_path, 'conf.py')
    print("hai i will now create a conf.py at %s" % conf_py_path)
    conf_py_template = jinja_env.get_template('conf.py')
    conf_py_file = open(conf_py_path, 'w')
    conf_py_file.write(conf_py_template.render(pkg_name=pkg['name'], doxygen_path=doxygen_path))
    conf_py_file.close()
    #run_shell_command("sphinx-build -b html . {0}".format(pkg_html_output_path), doc_path)
    ros2doc_path = os.path.abspath('.')  # yeah that's probably not great
    if ACTUALLY_RUN_DOCGEN:
        run_shell_command("{0}/sphinx3-build -b html . {1}".format(ros2doc_path, pkg_html_output_path), doc_path)
    pkg['generated'] = True  # we've built docs for this pkg

    pkg['parsed'].build_depends.sort(key=lambda x: x.name)
    pkg['parsed'].exec_depends.sort(key=lambda x: x.name)
    pkg['parsed'].test_depends.sort(key=lambda x: x.name)

    # now generate a summary page for this package
    summary_filename = os.path.join(html_output_path, 'summary', pkg['name']+'.html')
    summary_template = jinja_env.get_template('summary.html')
    summary_file = open(summary_filename, 'w')
    summary_file.write(summary_template.render(pkg=pkg))
    summary_file.close()

def make_index(index_filename, pkgs, jinja_env):
    index_template = jinja_env.get_template('index.html')
    print("creating index file at {0}".format(index_filename))
    index_file = open(index_filename, 'w')
    index_file.write(index_template.render(pkgs=pkgs))
    index_file.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Let's generate some docs!")
    parser.add_argument('src_path', metavar='SRC_PATH', type=str, nargs=1,
                        help='ROS 2 source tree')
    parser.add_argument('pkg', metavar='PKG', type=str, nargs='*',
                        help='package(s) to build docs')
    parser.add_argument('--all', action='store_true',
                        help='generate docs for all packages')
    args = parser.parse_args()
    print(args)

    jinja_env = jinja2.Environment(loader=jinja2.PackageLoader('ros2doc', 'templates'), autoescape=jinja_autoescape)
    now = datetime.datetime.now()
    buildpath = os.path.abspath(os.path.join('docbuild', now.strftime('%Y%m%d.%H%M%S')))
    os.makedirs(buildpath)
    update_symlink(buildpath, os.path.join('docbuild', 'latest'))

    pkgs_doc_path = os.path.join(buildpath, 'pkgs')
    os.makedirs(pkgs_doc_path)

    html_output_path = os.path.abspath(os.path.join(buildpath, 'html'))
    os.makedirs(html_output_path)

    summary_output_path = os.path.join(html_output_path, 'summary')
    os.makedirs(summary_output_path)

    pkgs = parse_pkgs()
    print("found {0} packages".format(len(pkgs)))
    pkgs.sort(key=lambda x: x['name'])

    for pkg in pkgs:
        # simple sanity check to avoid obvious badness in filesystem
        if pkg['name'][0] == '/' or '.' in pkg['name']:
            print("skipping illegal package name: [{0}]".format(pkg['name']))
            continue
        if args.all or (pkg['name'] in args.pkg):
            generate_pkg_doc(pkgs_doc_path, html_output_path, pkg, jinja_env)

    index_filename = os.path.join(html_output_path, 'index.html')
    make_index(index_filename, pkgs, jinja_env)
    print(pkgs[0]['parsed'])

