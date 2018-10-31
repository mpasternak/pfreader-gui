# -*- mode: python -*-

block_cipher = None


a = Analysis(['src/app.py'],
             pathex=['/Users/mpasternak/Programowanie/pfreader-gui'],
             binaries=[],
             datas=[('src/pfreader_gui/pfreader_gui.svg', 'pfreader_gui/')],
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
          name='app',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
app = BUNDLE(exe,
             name='app.app',
             icon=None,
             bundle_identifier=None)

