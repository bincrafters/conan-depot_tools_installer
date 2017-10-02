from conans import ConanFile, tools
import os


class DepotToolsConan(ConanFile):
    name = "depot_tools"
    version = "master"
    license = "Chromium"
    description = "A collection of tools for dealing with Chromium development"
    url = "https://github.com/SSE4/conan-depot_tools_installer"
    no_copy_source = True
    settings = {"os": ["Macos", "iOS"]}
    repository = "https://chromium.googlesource.com/chromium/tools/depot_tools.git"

    def source(self):
        if self.settings.os == "Macos" or self.settings.os == "iOS":
            self.run("git clone %s" % self.repository)
        else:
            raise Exception("unsupported os %s" % self.settings.os)

    def package(self):
        self.copy(pattern="*", dst=".", src=".")

    def package_info(self):
        bin_path = os.path.join(self.package_folder)
        self.env_info.path.append(bin_path)
