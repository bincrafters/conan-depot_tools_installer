#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
import os
import sys


class DepotToolsConan(ConanFile):
    name = "depot_tools_installer"
    version = "20190909"
    license = "BSD-3-Clause"
    description = "A collection of tools for dealing with Chromium development"
    url = "https://github.com/reneme/conan-depot_tools_installer"
    homepage = "https://chromium.googlesource.com/chromium/tools/depot_tools"
    author = "Bincrafters <bincrafters@gmail.com>"
    no_copy_source = True
    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if sys.version_info.major == 3:
            self.output.warn("Chromium depot_tools is not well supported by Python 3!")

    def source(self):
        commit = "e5641be5fe309f40aad850d4d1e1ca607768572c"
        tools.mkdir(self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            tools.get("{}/+archive/{}.tar.gz".format(self.homepage, commit))

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="bin", src=self._source_subfolder)

    def _fix_permissions(self):

        def chmod_plus_x(name):
            os.chmod(name, os.stat(name).st_mode | 0o111)

        if os.name == 'posix':
            for root, _, files in os.walk(os.path.join(self.package_folder, "bin")):
                for file in files:
                    filename = os.path.join(root, file)
                    with open(filename, 'rb') as f:
                        sig = f.read(4)
                        if type(sig) is str:
                            sig = [ord(s) for s in sig]
                        if len(sig) >= 2 and sig[0] == 0x23 and sig[1] == 0x21:
                            self.output.warn('chmod on script file %s' % file)
                            chmod_plus_x(filename)
                        elif sig == [0x7F, 0x45, 0x4C, 0x46]:
                            self.output.warn('chmod on ELF file %s' % file)
                            chmod_plus_x(filename)
                        elif \
                                sig == [0xCA, 0xFE, 0xBA, 0xBE] or \
                                sig == [0xBE, 0xBA, 0xFE, 0xCA] or \
                                sig == [0xFE, 0xED, 0xFA, 0xCF] or \
                                sig == [0xCF, 0xFA, 0xED, 0xFE] or \
                                sig == [0xFE, 0xED, 0xFA, 0xCE] or \
                                sig == [0xCE, 0xFA, 0xED, 0xFE]:
                            self.output.info('chmod on Mach-O file %s' % file)
                            chmod_plus_x(filename)

    def package_info(self):
        bin_folder = os.path.join(self.package_folder, "bin")
        self.output.info("Append %s to environment variable PATH" % bin_folder)
        self.env_info.PATH.append(bin_folder)
        # Don't update gclient automatically when running it
        self.env_info.DEPOT_TOOLS_UPDATE = "0"
        self._fix_permissions()