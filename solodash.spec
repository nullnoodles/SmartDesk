# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for SmartDesk.

Build command:
    pyinstaller solodash.spec --noconfirm

Excludes torch/sentence-transformers to keep the build size manageable.
The NLP clause classifier will show a graceful fallback message if the
model libraries aren't available.
"""

import sys
from pathlib import Path

block_cipher = None
ROOT = Path(SPECPATH)

a = Analysis(
    ['main.py'],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # Include assets (icon, splash)
        ('assets/icon.ico', 'assets'),
        ('assets/icon.png', 'assets'),
        ('assets/splash.png', 'assets'),
        # Include database schema
        ('app/data/schema.sql', 'app/data'),
        # Include trained ML models
        ('app/ml/models/*.pkl', 'app/ml/models'),
    ],
    hiddenimports=[
        'sklearn.ensemble',
        'sklearn.linear_model',
        'sklearn.preprocessing',
        'sklearn.tree._utils',
        'sklearn.neighbors._quad_tree',
        'statsmodels.tsa.arima.model',
        'PySide6.QtWidgets',
        'PySide6.QtCore',
        'PySide6.QtGui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy/unnecessary packages
        'torch',
        'torchvision',
        'torchaudio',
        'transformers',
        'sentence_transformers',
        'huggingface_hub',
        'tokenizers',
        'safetensors',
        'sympy',
        'tensorflow',
        'keras',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'py',
        'tkinter',
        'pyqtgraph',
        'plyer',
        'pytesseract',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SmartDesk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window — GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SmartDesk',
)
