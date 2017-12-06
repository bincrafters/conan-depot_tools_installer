from conans import ConanFile, tools
import os


class DepotToolsConan(ConanFile):
    name = "depot_tools"
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

    def package_info(self):
        bin_path = os.path.join(self.package_folder)
        self.env_info.path.append(bin_path)
