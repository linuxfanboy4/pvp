import os
import shutil
import tarfile
import zipfile
import urllib.request
import json
import sys
import hashlib
import subprocess
import platform
from pathlib import Path

class PVP:
    def __init__(self):
        self.package_db = Path("/usr/local/lib/pvp/packages/")
        self.bin_dir = Path("/usr/local/bin/")
        self.config_dir = Path(".")
        self.ensure_directories()

    def ensure_directories(self):
        try:
            self.package_db.mkdir(parents=True, exist_ok=True)
            self.bin_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error ensuring directories: {e}")
            sys.exit(1)

    def publish(self, config_file):
        config_path = self.config_dir / config_file
        if not config_path.exists():
            print(f"Error: Configuration file {config_file} not found.")
            return
        try:
            with open(config_path, 'r') as f:
                config = self.parse_package_config(f.read())
            if config:
                package_file = self.create_package(config)
                self.create_binary_package(package_file, config)
                print(f"Package {config['name']} published as {package_file}")
        except Exception as e:
            print(f"Error during publishing: {e}")

    def parse_package_config(self, config_data):
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(config_data)
            config = {
                "name": root.find('Name').text,
                "version": root.find('Version').text,
                "maintainer": root.find('Maintainer').text,
                "description": root.find('Description').text,
                "raw_link": root.find('RawLink').text,
                "section": root.find('Section').text
            }
            return config
        except Exception as e:
            print(f"Error parsing config: {e}")
            return None

    def create_package(self, config):
        package_filename = f"{config['name']}-{config['version']}.tar.gz"
        try:
            package_path = self.download_package(config['raw_link'], package_filename)
            return package_path
        except Exception as e:
            print(f"Error creating package: {e}")
            return None

    def download_package(self, url, filename):
        package_path = self.package_db / filename
        try:
            if not package_path.exists():
                urllib.request.urlretrieve(url, package_path)
            return package_path
        except Exception as e:
            print(f"Error downloading package from {url}: {e}")
            return None

    def create_binary_package(self, package_path, config):
        binary_name = f"{config['name']}-{config['version']}.pv"
        binary_path = self.package_db / binary_name
        try:
            with open(binary_path, 'w') as f:
                json.dump({
                    'name': config['name'],
                    'version': config['version'],
                    'maintainer': config['maintainer'],
                    'description': config['description'],
                    'raw_link': config['raw_link'],
                    'section': config['section'],
                    'source_file': str(package_path)
                }, f)
            os.chmod(binary_path, 0o755)
            self.create_symlink(config, binary_path)
        except Exception as e:
            print(f"Error creating binary package {binary_name}: {e}")

    def create_symlink(self, config, binary_path):
        symlink_name = self.bin_dir / f"{config['name']}.pykg"
        try:
            if symlink_name.exists():
                os.remove(symlink_name)
            os.symlink(binary_path, symlink_name)
        except Exception as e:
            print(f"Error creating symlink {symlink_name}: {e}")

    def install(self, package_file):
        package_path = self.package_db / package_file
        if not package_path.exists():
            print(f"Error: Package {package_file} not found.")
            return
        try:
            with open(package_path, 'r') as f:
                package_metadata = json.load(f)
            self.install_package_from_metadata(package_metadata)
        except Exception as e:
            print(f"Error installing package {package_file}: {e}")

    def install_package_from_metadata(self, metadata):
        package_file = Path(metadata['source_file'])
        try:
            if package_file.suffix == '.tar.gz':
                self.extract_tar_package(package_file)
            elif package_file.suffix == '.zip':
                self.extract_zip_package(package_file)
            else:
                print("Error: Unsupported package format.")
                return
            self.link_package(metadata)
        except Exception as e:
            print(f"Error installing package from metadata: {e}")

    def extract_tar_package(self, package_file):
        try:
            with tarfile.open(package_file, 'r:gz') as tar:
                tar.extractall(path=self.package_db)
        except Exception as e:
            print(f"Error extracting tar package {package_file}: {e}")

    def extract_zip_package(self, package_file):
        try:
            with zipfile.ZipFile(package_file, 'r') as zip_ref:
                zip_ref.extractall(path=self.package_db)
        except Exception as e:
            print(f"Error extracting zip package {package_file}: {e}")

    def link_package(self, metadata):
        package_dir = self.package_db / f"{metadata['name']}-{metadata['version']}"
        try:
            if not package_dir.exists():
                print(f"Error: Failed to extract package {metadata['name']}.")
                return
            symlink_target = self.bin_dir / f"{metadata['name']}.pykg"
            if symlink_target.exists():
                os.remove(symlink_target)
            os.symlink(package_dir, symlink_target)
        except Exception as e:
            print(f"Error linking package {metadata['name']}: {e}")

    def uninstall(self, package_name):
        symlink_target = self.bin_dir / f"{package_name}.pykg"
        try:
            if symlink_target.exists():
                package_metadata = self.read_package_metadata(symlink_target)
                self.remove_symlink(symlink_target)
                self.remove_package_files(package_metadata)
                print(f"Package {package_name} uninstalled successfully.")
            else:
                print(f"Error: Package {package_name} not found.")
        except Exception as e:
            print(f"Error uninstalling package {package_name}: {e}")

    def read_package_metadata(self, symlink_target):
        try:
            with open(symlink_target, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading package metadata: {e}")
            return {}

    def remove_symlink(self, symlink_target):
        try:
            if symlink_target.exists():
                os.remove(symlink_target)
        except Exception as e:
            print(f"Error removing symlink {symlink_target}: {e}")

    def remove_package_files(self, metadata):
        package_dir = self.package_db / f"{metadata['name']}-{metadata['version']}"
        try:
            if package_dir.exists():
                shutil.rmtree(package_dir)
        except Exception as e:
            print(f"Error removing package files for {metadata['name']}: {e}")

    def upgrade(self, package_name):
        symlink_target = self.bin_dir / f"{package_name}.pykg"
        try:
            if symlink_target.exists():
                package_metadata = self.read_package_metadata(symlink_target)
                self.uninstall(package_name)
                self.install(symlink_target.name)
                print(f"Package {package_name} upgraded successfully.")
            else:
                print(f"Error: Package {package_name} not installed.")
        except Exception as e:
            print(f"Error upgrading package {package_name}: {e}")

    def search_installed(self, search_term):
        installed_packages = [f for f in os.listdir(self.bin_dir) if f.endswith('.pykg')]
        result = []
        try:
            for pkg in installed_packages:
                metadata = self.read_package_metadata(self.bin_dir / pkg)
                if search_term.lower() in metadata['name'].lower():
                    result.append(metadata)
            if result:
                print(f"Found {len(result)} package(s) matching '{search_term}':")
                for pkg in result:
                    self.show_package_details(pkg)
            else:
                print(f"No packages found for '{search_term}'.")
        except Exception as e:
            print(f"Error searching for packages: {e}")

    def show_package_details(self, metadata):
        try:
            print(f"Name: {metadata['name']}")
            print(f"Version: {metadata['version']}")
            print(f"Maintainer: {metadata['maintainer']}")
            print(f"Description: {metadata['description']}")
            print(f"Raw Link: {metadata['raw_link']}")
            print(f"Section: {metadata['section']}")
            print("-" * 40)
        except Exception as e:
            print(f"Error displaying package details: {e}")

def main():
    pvp = PVP()
    if len(sys.argv) < 2:
        print("Usage: pvp <command> [args]")
        return

    command = sys.argv[1]
    try:
        if command == 'publish':
            if len(sys.argv) != 3:
                print("Usage: pvp publish <config_file>")
            else:
                pvp.publish(sys.argv[2])
        elif command == 'install':
            if len(sys.argv) != 3:
                print("Usage: pvp install <package_name>")
            else:
                pvp.install(sys.argv[2])
        elif command == 'uninstall':
            if len(sys.argv) != 3:
                print("Usage: pvp uninstall <package_name>")
            else:
                pvp.uninstall(sys.argv[2])
        elif command == 'upgrade':
            if len(sys.argv) != 3:
                print("Usage: pvp upgrade <package_name>")
            else:
                pvp.upgrade(sys.argv[2])
        elif command == 'search':
            if len(sys.argv) != 3:
                print("Usage: pvp search <search_term>")
            else:
                pvp.search_installed(sys.argv[2])
        else:
            print("Unknown command.")
    except Exception as e:
        print(f"Error executing command {command}: {e}")

if __name__ == "__main__":
    main()
