import os
import zipfile
import urllib.request
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop
import shutil
import glob
import stat

def download_binaries(target_base_dir):
    dynawo_version = '1.7.0'
    dynawo_github_url = "https://github.com/dynawo/dynaflow-launcher"
    linux_url = f"{dynawo_github_url}/releases/download/v{dynawo_version}/DynaFlowLauncher_Linux_centos7_v{dynawo_version}.zip"
    windows_url = f"{dynawo_github_url}/releases/download/v{dynawo_version}/DynaFlowLauncher_Windows_v{dynawo_version}.zip"

    url = windows_url if os.name == 'nt' else linux_url
    target_dir = os.path.join(target_base_dir, "dynawo", "dynawo")
    zip_path = "dynawo_tmp.zip"
    temp_extract_dir = "temp_extract"

    urllib.request.urlretrieve(url, zip_path)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_extract_dir)

    extracted_folder = os.path.join(temp_extract_dir, "dynaflow-launcher")

    if os.path.exists(extracted_folder):
        for item in os.listdir(extracted_folder):
            src = os.path.join(extracted_folder, item)
            dst = os.path.join(target_dir, item)
            if os.path.exists(dst):
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                else:
                    os.remove(dst)
            shutil.move(src, dst)

    # Fix file permissions on Linux/Unix systems
    if os.name != 'nt':
        shell_scripts = [
            os.path.join(target_dir, "dynawo.sh"),
            os.path.join(target_dir, "dynawo-algorithms.sh"),
            os.path.join(target_dir, "dynaflow-launcher.sh")
        ]
        for script in shell_scripts:
            if os.path.exists(script):
                os.chmod(script, os.stat(script).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        for bin_dir in ["bin", "sbin"]:
            bin_path = os.path.join(target_dir, bin_dir)
            if os.path.exists(bin_path):
                for file in os.listdir(bin_path):
                    file_path = os.path.join(bin_path, file)
                    if os.path.isfile(file_path) and not file.endswith('.cmake'):
                        os.chmod(file_path, os.stat(file_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    problematic_patterns = [
        "OpenModelica/lib/x86_64-linux-gnu/omc/libModelicaStandardTables.so*",
        "OpenModelica/lib/x86_64-linux-gnu/omc/libModelicaIO.so*",
        "OpenModelica/lib/x86_64-linux-gnu/omc/libModelicaMatIO.so*"
    ]

    for pattern in problematic_patterns:
        full_pattern = os.path.join(target_dir, pattern)
        matched_files = glob.glob(full_pattern)

        if matched_files:
            for file_path in matched_files:
                os.remove(file_path)

    shutil.rmtree(temp_extract_dir)

    os.remove(zip_path)

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        download_binaries(self.install_lib)

class PostDevelopCommand(develop):
    def run(self):
        develop.run(self)
        download_binaries(os.path.abspath("."))

setup(
    zip_safe=False,
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
    },
)