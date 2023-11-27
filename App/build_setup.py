from cx_Freeze import setup, Executable

base = "Win32GUI"

build_exe_options = {
    'includes': ["sqlalchemy.dialects.postgresql",
                 "canmatrix.formats.dbc"],
    'include_files': [('src', 'src')],
}

setup(
    name="MF4toGrafana_v3",
    version="1.0",
    description="MF4 Converter",
    options={"build_exe": build_exe_options},
    executables=[Executable("MF4toGrafana_v3.py", base=base)],
)
