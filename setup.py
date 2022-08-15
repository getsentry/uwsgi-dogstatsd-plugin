from __future__ import annotations

import os.path
import subprocess
import sys

from setuptools import Command
from setuptools import setup
from setuptools.command.build import build as _build
from setuptools.command.install import install as _install
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

if not os.path.exists("uwsgi-dogstatsd/LICENSE"):
    raise SystemExit("run `git submodule update --init`")


class bdist_wheel(_bdist_wheel):
    def finalize_options(self):
        super().finalize_options()
        self.root_is_pure = False

    def get_tag(self):
        return "py2.py3", "none", super().get_tag()[-1]


class build(_build):
    sub_commands = _build.sub_commands + [("build_plugin", None)]


class build_plugin(Command):
    def initialize_options(self):
        self.build_temp = None

    def finalize_options(self):
        self.set_undefined_options("build", ("build_temp", "build_temp"))

    def run(self):
        libdir = os.path.join(self.build_temp, "lib")
        os.makedirs(libdir, exist_ok=True)
        subprocess.check_call(
            (
                sys.executable,
                "-c",
                "import pyuwsgi; pyuwsgi.run()",
                "--build-plugin",
                os.path.abspath("uwsgi-dogstatsd"),
            ),
            cwd=libdir,
        )


class install(_install):
    sub_commands = _install.sub_commands + [("install_plugin", None)]


class install_plugin(Command):
    def initialize_options(self):
        self.build_temp = self.install_data = None
        self.outfiles = []

    def finalize_options(self):
        self.set_undefined_options("build", ("build_temp", "build_temp"))
        self.set_undefined_options("install", ("install_data", "install_data"))

    def run(self):
        src = os.path.join(self.build_temp, "lib", "dogstatsd_plugin.so")
        dst = os.path.join(self.install_data, "lib", "dogstatsd_plugin.so")
        os.makedirs(os.path.dirname(dst))
        self.outfiles = self.copy_file(src, dst)

    def get_outputs(self):
        return self.outfiles


setup(
    cmdclass={
        "bdist_wheel": bdist_wheel,
        "build": build,
        "build_plugin": build_plugin,
        "install": install,
        "install_plugin": install_plugin,
    },
)
