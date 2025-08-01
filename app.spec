# -*- mode: python ; coding: utf-8 -*-

import os
import pathlib
from PyInstaller.utils.hooks import collect_data_files

project_root = str(pathlib.Path().resolve())

datas = [
    # Required folders
    (os.path.join(project_root, 'Laser_Perfect_Colored'), 'Laser_Perfect_Colored'),
    (os.path.join(project_root, 'Laser_Defects_Colored'), 'Laser_Defects_Colored'),
    (os.path.join(project_root, 'Laser Defects'), 'Laser Defects'),
    (os.path.join(project_root, 'outputs'), 'outputs'),

    # Frontend
    (os.path.join(project_root, 'frontend', 'static'), 'frontend/static'),
    (os.path.join(project_root, 'frontend', 'templates'), 'frontend/templates'),
] + collect_data_files('PIL')  # for Pillow image support

block_cipher = None

a = Analysis(
    ['backend/app.py'],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=['jinja2.ext'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DefectPlacementTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='DefectPlacementTool'
)
