import os
import zipfile
import urllib.request
from setuptools import build_meta as _orig
import shutil
import glob

dynawo_version='1.7.0'
dynawo_github_url = "https://github.com/dynawo/dynaflow-launcher"
linux_url = f"{dynawo_github_url}/releases/download/v{dynawo_version}/DynaFlowLauncher_Linux_centos7_v{dynawo_version}.zip"
windows_url = f"{dynawo_github_url}/releases/download/v{dynawo_version}/DynaFlowLauncher_Windows_v{dynawo_version}.zip"

def download_binaries():
    url = windows_url if os.name == 'nt' else linux_url
    target_dir = os.path.join(os.path.dirname(__file__), "dynawo")
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

class _CustomBuildMeta:
    def __getattr__(self, name):
        return getattr(_orig, name)

    def build_wheel(self, wheel_directory, config_settings=None, metadata_directory=None):
        download_binaries()
        return _orig.build_wheel(wheel_directory, config_settings, metadata_directory)

    def build_sdist(self, sdist_directory, config_settings=None):
        download_binaries()
        return _orig.build_sdist(sdist_directory, config_settings)


build_wheel = _CustomBuildMeta().build_wheel
build_sdist = _CustomBuildMeta().build_sdist
get_requires_for_build_wheel = _orig.get_requires_for_build_wheel
get_requires_for_build_sdist = _orig.get_requires_for_build_sdist
prepare_metadata_for_build_wheel = _orig.prepare_metadata_for_build_wheel