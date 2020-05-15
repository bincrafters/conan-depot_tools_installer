from conans import ConanFile, tools
from conans.tools import os_info
import os
import sys
import shutil


class DepotToolsConan(ConanFile):
    name = "depot_tools_installer"
    version = "20200515"
    _commit = "5e0a4a6b8088fc55794b51d1919c13ac4ae6ef0c"
    license = "BSD-3-Clause"
    description = "A collection of tools for dealing with Chromium development"
    url = "https://github.com/bincrafters/conan-depot_tools_installer"
    homepage = "https://chromium.googlesource.com/chromium/tools/depot_tools"
    no_copy_source = True
    short_paths = True
    settings = "os_build"
    _source_subfolder = "source_subfolder"

    def configure(self):
        if sys.version_info.major == 3:
            self.output.warn("Chromium depot_tools is not well supported by Python 3!")

    def _dereference_symlinks(self):
        """
        Windows 10 started to introduce support for symbolic links. Unfortunately
        it caused a lot of trouble during packaging. Namely, opening symlinks causes
        `OSError: Invalid argument` rather than actually following the symlinks.
        Therefore, this workaround simply copies the destination file over the symlink
        """
        if self.settings.os_build != "Windows":
            return

        for root, dirs, files in os.walk(self._source_subfolder):
            symlinks = [os.path.join(root, f) for f in files if os.path.islink(os.path.join(root, f))]
            for symlink in symlinks:
                dest = os.readlink(symlink)
                os.remove(symlink)
                shutil.copy(os.path.join(root, dest), symlink, follow_symlinks=False)
                self.output.info("Replaced symlink '%s' with its destination file '%s'" % (symlink, dest))

    def source(self):
        tools.mkdir(self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            tools.get("{}/+archive/{}.tar.gz".format(self.homepage, self._commit))
        self._dereference_symlinks()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="bin", src=self._source_subfolder)
        self._fix_permissions()

    def _fix_permissions(self):

        def chmod_plus_x(name):
            os.chmod(name, os.stat(name).st_mode | 0o111)

        if self.settings.os_build != "Windows":
            for root, _, files in os.walk(self.package_folder):
                for file_it in files:
                    filename = os.path.join(root, file_it)
                    with open(filename, 'rb') as f:
                        sig = f.read(4)
                        if type(sig) is str:
                            sig = [ord(s) for s in sig]
                        if len(sig) >= 2 and sig[0] == 0x23 and sig[1] == 0x21:
                            self.output.info('chmod on script file %s' % file_it)
                            chmod_plus_x(filename)
                        elif sig == [0x7F, 0x45, 0x4C, 0x46]:
                            self.output.info('chmod on ELF file %s' % file_it)
                            chmod_plus_x(filename)
                        elif \
                                sig == [0xCA, 0xFE, 0xBA, 0xBE] or \
                                sig == [0xBE, 0xBA, 0xFE, 0xCA] or \
                                sig == [0xFE, 0xED, 0xFA, 0xCF] or \
                                sig == [0xCF, 0xFA, 0xED, 0xFE] or \
                                sig == [0xFE, 0xED, 0xFA, 0xCE] or \
                                sig == [0xCE, 0xFA, 0xED, 0xFE]:
                            self.output.info('chmod on Mach-O file %s' % file_it)
                            chmod_plus_x(filename)

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        # Don't update gclient automatically when running it
        self.env_info.DEPOT_TOOLS_UPDATE = "0"
