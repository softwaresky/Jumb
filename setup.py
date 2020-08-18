import sys
import os
import platform

from cx_Freeze import setup, Executable


def make_build(script_target=""):

    include_files = []

    img_dir = os.path.abspath("./imgs/dice")
    for img_ in os.listdir(img_dir):
        pair = (os.path.join(img_dir, img_), "imgs/dice/{0}".format(img_))
        include_files.append(pair)

    # dependencies
    build_exe_options = {
        # "os", "sys", "PySide2.QtCore", "PySide2.QtWidgets","PySide2.QtGui", "shiboken2"
        "packages": ["os", "sys"],
        "include_files": include_files,
        "excludes": ["Tkinter", "Tkconstants", "tcl", ],
        "includes": ["PySide2.QtCore", "PySide2.QtWidgets","PySide2.QtGui", "shiboken2"],
        "build_exe": "./build_script/Jamb-x64"
    }

    executable = [
        Executable(r"{0}".format(script_target),
                   base="Win32GUI",
                   targetName="Jamb.exe")
    ]

    setup(
        name="Jamb",
        version="0.1",
        description="Jamb!",
        author="Softwaresky",
        options={"build_exe": build_exe_options},
        executables=executable
    )

def main():
    sys.argv.append("build")
    script_target = os.path.abspath("./Jumb.py")
    make_build(script_target=script_target)

main()