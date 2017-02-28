#!/usr/bin/env python3
import ament_package
import ament_tools.verbs.list_packages
from ament_tools.package_types import parse_package
import os
import shutil
import datetime

dt = datetime.datetime.now()
buildpath = os.path.join('docbuild', dt.strftime('%Y%m%d.%H%M'))
os.makedirs(buildpath)

pkgs_doc_path = os.path.join(buildpath, 'pkgs')
if not os.path.exists(pkgs_doc_path):
  os.makedirs(pkgs_doc_path)

basepath = '.'
pkg_paths = ament_tools.verbs.list_packages.find_package_paths(basepath)
for pkg_path in pkg_paths:
  pkg_abspath = os.path.join(basepath, pkg_path)
  pkg = parse_package(pkg_abspath)
  print(pkg.name)
  if pkg.name != 'joy':
    continue
  pkg_doc_path = os.path.join(pkgs_doc_path, pkg.name)
  if os.path.exists(pkg_doc_path):
    continue
  shutil.copytree(pkg_abspath, pkg_doc_path)
  if os.path.exists(os.path.join(pkg_doc_path, 'doc')):
    # hooray there is a doc directory. let's create a conf.py in there
