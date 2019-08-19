import os
from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
from nxtools import NxConanFile
from glob import glob

class IcuConan(NxConanFile):
    name = "icu"
    version = "64.2"
    tarball_name = "%s4c-%s-src.tgz" % (name, version.replace('.','_'))
    license = "ICU"
    author = "hoxnox <hoxnox@gmail.com>"
    url = "https://github.com/hoxnox/conan-icu"
    description = "ICU is a mature, widely used set of C/C++ and Java libraries " \
                  "providing Unicode and Globalization support for software applications."
    topics = ("icu", "unicode")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared":    [True, False], \
               "extras":    [True, False], \
               "icuio":     [True, False], \
               "layoutex":  [True, False] }
    default_options = "shared=False", \
                      "extras=False", \
                      "icuio=False", \
                      "layoutex=False"
    generators = "cmake"

    def do_source(self):
        self.retrieve("627d5d8478e6d96fc8c90fed4851239079a561a6a8b9e48b0892f24e82d31d6c",
                [
                    "vendor://unicode.org/icu/%s" % self.tarball_name,
                    "https://github.com/unicode-org/icu/releases/download/release-%s/%s"
                        % (self.version.replace('.','-'), self.tarball_name)
                ], self.tarball_name)

    def do_build(self):
        build_dir = "{staging_dir}/src".format(staging_dir=self.staging_dir)
        tools.untargz(self.tarball_name, build_dir)
        os.unlink(self.tarball_name)

        src_dir = "{staging_dir}/src/icu".format(staging_dir=self.staging_dir, v=self.version)
        for file in sorted(glob("patch/[0-9]*.patch")):
            self.output.info("Applying patch '{file}'".format(file=file))
            tools.patch(base_path=src_dir, patch_file=file, strip=0)

        env_build = AutoToolsBuildEnvironment(self)
        if not self.options.get_safe("shared"):
            env_build.defines.append("U_STATIC_IMPLEMENTATION")
        with tools.environment_append(env_build.vars):
            self.run("cd {build_dir}/icu/source && CXX={compiler} CC={compiler} ./configure --prefix=\"{staging}\""
                     " --enable-tools=no --enable-tests=no --enable-samples=no --disable-renaming --disable-debug --with-data-packaging=static --with-library-bits=64"
                     " {shared} {extras} {icuio} {layoutex}".format(
                         compiler = self.settings.compiler, 
                         shared="--enable-shared --disable-static" if self.options.shared else "--enable-static --disable-shared",
                         extras="--enable-extras=yes" if self.options.extras else "--enable-extras=no",
                         icuio="--enable-icuio=yes" if self.options.icuio else "--enable-icuio=no",
                         layoutex="--enable-layoutex=yes" if self.options.layoutex else "--enable-layoutex=no",
                         build_dir=build_dir,
                         staging=self.staging_dir))
            self.run("cd %s/icu/source && make install" % build_dir)


    def do_package_info(self):
        self.cpp_info.libs = ["icuuc", "icui18n", "icudata"]

