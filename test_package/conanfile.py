from conans import ConanFile
import os


class TestPackage(ConanFile):

    def test(self):
        self.run("gclient --version", run_environment=True)
