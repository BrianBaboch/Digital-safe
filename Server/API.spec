# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['API.py'],
             pathex=['C:\\Users\\Brian Baboch\\Desktop\\My Files\\France\\Telecom Paris\\2eme Année\\SR2I\\SR2I206 - Infrastructure de confiance et mise en oeuvre\\Projet\\Code\\Server'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='API',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
