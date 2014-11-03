"""Setup file for freezing Evo application with cx_Freeze.

This file has been downloaded form gnome wiki and modified for
Evo application.

To freeze excute:
$ setup.py build
"""

import os, site, sys
from cx_Freeze import setup, Executable

## Get the site-package folder, not everybody will install
## Python into C:\PythonXX
site_dir = site.getsitepackages()[1]
include_dll_path = os.path.join(site_dir, "gnome")

## Collect the list of missing dll when cx_freeze builds the app
missing_dll = ['libatk-1.0-0.dll',
               'libcairo-gobject-2.dll',
               'libffi-6.dll',
               'libfontconfig-1.dll',
               'libfreetype-6.dll',
               'libgailutil-3-0.dll',
               'libgcrypt-11.dll',
               'libgdk-3-0.dll',
               'libgdk_pixbuf-2.0-0.dll',
               'libgio-2.0-0.dll',
               'libgirepository-1.0-1.dll',
               'libgladeui-2-4.dll',
               'libglib-2.0-0.dll',
               'libgmodule-2.0-0.dll',
               'libgnutls-26.dll',
               'libgobject-2.0-0.dll',
               'libgthread-2.0-0.dll',
               'libgtk-3-0.dll',
               'libharfbuzz-gobject-0.dll',
               'libintl-8.dll',
               'libjpeg-8.dll',
               'libp11-kit-0.dll',
               'libpango-1.0-0.dll',
               'libpangocairo-1.0-0.dll',
               'libpangoft2-1.0-0.dll',
               'libpangowin32-1.0-0.dll',
               'libpng16-16.dll',
               'libpyglib-gi-2.0-python34-0.dll',
               'librsvg-2-2.dll',
               'libwebp-4.dll',
               'libwinpthread-1.dll',
               'libxml2-2.dll',
               'libzzz.dll'
               ]

## We also need to add the glade folder, cx_freeze will walk
## into it and copy all the necessary files
#glade_folder = 'glade'

## We need to add all the libraries too (for themes, etc..)
gtk_libs = ['etc', 'lib', 'share']

## Create the list of includes as cx_freeze likes
include_files = []
for dll in missing_dll:
    if os.path.isfile(r'%s' % os.path.join(include_dll_path, dll)):
        include_files.append((os.path.join(include_dll_path, dll), dll))

## Let's add glade folder and files
#include_files.append((glade_folder, glade_folder))

## Let's add gtk libraries folders and files
for lib in gtk_libs:
    include_files.append((os.path.join(include_dll_path, lib), lib))

## Evo files
cur_dir = os.path.dirname(__file__)
include_files.append((os.path.join(cur_dir, 'data'), 'data'))
include_files.append((os.path.join(cur_dir, 'Doc'), 'Doc'))
include_files.append((os.path.join(cur_dir, 'config.ini'), 'config.ini'))
include_files.append((os.path.join(cur_dir, 'config.ini'), 'Evo.glade'))
include_files.append((os.path.join(cur_dir, 'config.ini'), 'Evo.ico'))

base = None

## Lets not open the console while running the app
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable("Evo.pyw",
               base=base,
               icon="Evo.ico"
    )
]

buildOptions = dict(
    compressed = True,
    includes = ["gi"],
    packages = ["gi"],
    include_files = include_files
    )

setup(
    name = "Evo",
    author = "Mahan Marwat",
    version = "1.0.0",
    description = "GUI application for PTCL Evo Wingle",
    options = dict(build_exe = buildOptions),
    executables = executables
)
