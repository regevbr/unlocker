#!/usr/bin/env python3
"""
The MIT License (MIT)

Copyright (c) 2015-2021 Dave Parsons

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the 'Software'), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import os
import sys
import tarfile
import time
from urllib.request import urlopen
from urllib.request import urlretrieve
from xml.etree import ElementTree
from zipfile import ZipFile

ROOT = os.path.dirname(os.path.abspath(__file__))
TOOL_PATH = ROOT + '/tools/'

# Download redirects
# GET_FUSION = 'https://vmware.com/go/getfusion'
# GET_WORKSTATION_WIN = 'https://www.vmware.com/go/getworkstation-win'
# GET_WORKSTATION_LINUX = 'https://www.vmware.com/go/getworkstation-linux'
# GET_PLAYER_WIN = 'https://www.vmware.com/go/getplayer-win'
# GET_PLAYER_LINUX = 'https://www.vmware.com/go/getplayer-linux'

# VMWARE CDS FOR UPDATES
VMWARE_CDS = 'https://softwareupdate.vmware.com/cds/vmw-desktop/'
FUSION_XML = VMWARE_CDS + 'fusion.xml'
FUSION_TAR = 'com.vmware.fusion.zip.tar'
FUSION_ZIP = 'com.vmware.fusion.zip'
FUSION_TAR_PATH = TOOL_PATH + FUSION_TAR
FUSION_ZIP_PATH = TOOL_PATH + FUSION_ZIP
DARWIN_ISO_ZIP = 'payload/VMware Fusion.app/Contents/Library/isoimages/darwin.iso'
DARWINPRE15_ISO_ZIP = 'payload/VMware Fusion.app/Contents/Library/isoimages/darwinPre15.iso'
DARWIN_ISO_PATH = TOOL_PATH + 'darwin.iso'
DARWINPRE15_ISO_PATH = TOOL_PATH + 'darwinPre15.iso'


class MyProgressBar:
    def __init__(self):
        self.start_time = time.time()

    def __call__(self, block_num, block_size, total_size):
        if block_num == 0:
            self.start_time = time.time()
            return
        duration = time.time() - self.start_time
        progress_size = int(block_num * block_size)
        speed = int(progress_size / (1024 * duration)) if duration > 0 else 0
        percent = min(int(block_num * block_size * 100 / total_size), 100)
        time_remaining = ((total_size - progress_size) / 1024) / speed if speed > 0 else 0
        sys.stdout.write(f'\r'
                         f'{percent:.1f}%, '
                         f'{progress_size / (1024 * 1024):.1f} MB, '
                         f'{speed:.1f} KB/s, '
                         f'{time_remaining:.1f} seconds remaining')
        sys.stdout.flush()
        return


def parse_fusion_xml(fusion_xml):
    # Parse the Fusion directory page looking for highest build number
    tree = ElementTree.fromstring(fusion_xml)
    all_urls = tree.findall('.//url')
    build = 0
    file = ''
    for url in all_urls:
        parts = url.text.split('/')
        if parts[0] == 'info-only':
            # Ignore a Fusion 4.0 test folder
            continue
        current_build = int(parts[2])
        if current_build > build:
            build = current_build
            parts[4] = FUSION_TAR
            file = VMWARE_CDS + '/'.join(parts)

    return build, file


def main():
    # Check minimal Python version is 3.8
    if sys.version_info < (3, 8):
        sys.stderr.write('You need Python 3.8 or later\n')
        sys.exit(1)

    # Make a tools folder if not present
    if not os.path.exists(TOOL_PATH):
        os.makedirs(TOOL_PATH)

    # Get the list of Fusion releases
    response = urlopen(FUSION_XML)
    fusion_xml = response.read()
    build, file_path = parse_fusion_xml(fusion_xml)

    # Download the com.vmware.fusion.zip.tar file
    print(f'Retrieving Fusion build {build} from: {file_path}')
    urlretrieve(file_path, FUSION_TAR_PATH, MyProgressBar())
    print('\n')

    # Extract the zip from tar
    tar = tarfile.open(FUSION_TAR_PATH, 'r')
    tar.extract(FUSION_ZIP, path=TOOL_PATH)
    tar.close()

    # Extract the iso files from VMWare Fusion.app
    with ZipFile(FUSION_ZIP_PATH, 'r') as zipObj:
        zipinfo = zipObj.getinfo(DARWIN_ISO_ZIP)
        zipinfo.filename = os.path.basename(DARWIN_ISO_PATH)
        zipObj.extract(zipinfo, os.path.dirname(os.path.realpath(DARWIN_ISO_PATH)))
        zipinfo = zipObj.getinfo(DARWINPRE15_ISO_ZIP)
        zipinfo.filename = os.path.basename(DARWINPRE15_ISO_PATH)
        zipObj.extract(zipinfo, os.path.dirname(os.path.realpath(DARWINPRE15_ISO_PATH)))

    # Cleanup working files and folders
    os.remove(FUSION_TAR_PATH)
    os.remove(FUSION_ZIP_PATH)

    return


if __name__ == '__main__':
    main()
