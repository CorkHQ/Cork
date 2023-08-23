from zipfile import ZipFile
from urllib import request
from joblib import Parallel, delayed
from io import BytesIO
import logging
import hashlib
import shutil
import os
from cork.roblox import packages, cdn

def install(version, version_directory, version_channel, version_type, state_dictionary={}, download_threads = 2, install_threads = -1):
    if os.path.isdir(version_directory):
        shutil.rmtree(version_directory)

    os.makedirs(version_directory)

    package_dictionary, package_manifest = packages.get(version_type, version, version_channel, cdn.get())
    package_zips = {}

    state_dictionary["state"] = "downloading"
    def download(package, package_url, target):
        logging.info(f"Downloading package {package}...")

        attempts = 0
        success = False
        while attempts < 3 and success == False:
            try:
                response = request.urlopen(request.Request(
                    package_url, headers={"User-Agent": "Cork"}))
                response_bytes = response.read()

                if package_manifest[package][0] != hashlib.md5(response_bytes).hexdigest():
                    raise ConnectionError(f"Checksum failed for {package}")
                
                success = True
            except:
                attempts += 1
                if attempts >= 3:
                    raise ConnectionError(f"Failed to download {package}")
                else:
                    logging.error(f"Download failed for {package}, retrying...")

        zip = ZipFile(BytesIO(response_bytes))
        package_zips[(package, target)] = zip

        state_dictionary["packages_downloaded"] += 1

    state_dictionary["packages_downloaded"] = 0
    state_dictionary["packages_installed"] = 0
    state_dictionary["packages_total"] = len(package_dictionary)

    if download_threads == 0:
        download_threads = len(package_dictionary)
    
    Parallel(n_jobs=download_threads, require='sharedmem')(
        delayed(download)(package, package_url, target) for (package, package_url), target in package_dictionary.items())

    def install(package, target, zip):
        logging.info(f"Installing package {package}...")

        target_directory = os.path.join(version_directory, target)
        if not os.path.isdir(target_directory):
            os.makedirs(target_directory)

        for zipinfo in zip.infolist():
            zipinfo.filename = zipinfo.filename.replace("\\", "/")
            zip.extract(zipinfo, target_directory)
        
        state_dictionary["packages_installed"] += 1

    if install_threads == 0:
        install_threads = len(package_dictionary)
    
    state_dictionary["state"] = "installing"
    Parallel(n_jobs=install_threads, require='sharedmem')(delayed(install)(
        package, target, zip) for (package, target), zip in package_zips.items())

    with open(os.path.join(version_directory, "AppSettings.xml"), "w") as file:
        file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n" +
                   "<Settings>\r\n" +
                   "        <ContentFolder>content</ContentFolder>\r\n" +
                   "        <BaseUrl>http://www.roblox.com</BaseUrl>\r\n" +
                   "</Settings>\r\n"
                   )
