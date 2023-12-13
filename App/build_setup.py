# docs:
# https://cx-freeze.readthedocs.io/en/stable/setup_script.html

from cx_Freeze import setup, Executable

base = "Win32GUI"

executables = (
    [
        Executable(
            "MF4toGrafana_v3.py",
            base=base,
            uac_admin=True,
            icon="src\media\icon-logo.ico",
            target_name="BobLoader MF4"
        )
    ]
)

build_exe_options = {
    # set build output directory
    'build_exe': "build\BobLoader MF4",
    # include libraries
    'includes': ["sqlalchemy.dialects.postgresql",
                 "canmatrix.formats.dbc"],
    # include files
    'include_files': [('src\media', 'src\media'), ('src\config.json', 'src\config.json')],
}

setup(
    name="BobLoader MF4",
    version="1.0",
    description="MF4 file converter, uploader and downloader",
    executables=executables,
    options={
        "build_exe": build_exe_options
    },
)
