#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
import os


class DepotToolsConan(ConanFile):
    name = "depot_tools_installer"
    version = "master"
    license = "Chromium"
    description = "A collection of tools for dealing with Chromium development"
    url = "https://github.com/SSE4/conan-depot_tools_installer"
    no_copy_source = True
    short_paths = True
    settings = {"os"}
    repository = "https://chromium.googlesource.com/chromium/tools/depot_tools.git"

    def system_requirements(self):
        if self.settings.os == "Linux":
            if str(tools.os_info.linux_distro) in ["ubuntu", "debian"]:
                installer = tools.SystemPackageTool()
                installer.install('ca-certificates')

    def source(self):
        if self.settings.os == "Windows":
            url = "https://storage.googleapis.com/chrome-infra/depot_tools.zip"
            tools.get(url)
        else:
            self.run("git clone %s" % self.repository)

    def package(self):
        self.copy(pattern="*", dst=".", src=".")

    def fix_permissions(self):
        def chmod_plus_x(name):
            os.chmod(name, os.stat(name).st_mode | 0o111)

        if os.name == 'posix':
            for root, _, files in os.walk(self.package_folder):
                for file in files:
                    filename = os.path.join(root, file)
                    with open(filename, 'rb') as f:
                        sig = f.read(4)
                        if len(sig) >= 2 and sig[0] == 0x23 and sig[1] == 0x21:
                            self.output.warn('chmod on script file %s' % file)
                            chmod_plus_x(filename)
                        elif sig == [0x7F, 0x45, 0x4C, 0x46]:
                            self.output.warn('chmod on ELF file %s' % file)
                            chmod_plus_x(filename)
                        elif \
                                sig == [0xCA, 0xFE, 0xBA, 0xBE] or \
                                sig == [0xBE, 0xBA, 0xFE, 0xCA] or \
                                sig == [0xFE, 0xED, 0xFA, 0xCE] or \
                                sig == [0xCE, 0xFA, 0xED, 0xFE]:
                            self.output.warn('chmod on Mach-O file %s' % file)
                            chmod_plus_x(filename)

    def package_info(self):
        self.fix_permissions()
        self.env_info.path.append(self.package_folder)
