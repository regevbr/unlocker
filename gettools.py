#!/usr/bin/env python
"""
The MIT License (MIT)

Copyright (c) 2015-2017 Dave Parsons

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

from progressbar import ProgressBar
from urllib.request import urlopen
from urllib.request import urlretrieve
from xml.etree import ElementTree
from zipfile import ZipFile


ROOT = os.path.dirname(os.path.abspath(__file__))
TOOL_PATH = ROOT + '/tools/'
GET_FUSION = 'https://vmware.com/go/getfusion'
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
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        if not self.pbar:
            self.pbar = ProgressBar(maxval=total_size)
            self.pbar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()


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
            print(parts[2])
            build = current_build
            parts[4] = FUSION_TAR
            file = VMWARE_CDS + '/'.join(parts)

    return build, file


def main():
    # Check minimal Python version is 3.8
    if sys.version_info < (3, 8):
        sys.stderr.write('You need Python 3.8 or later\n')
        sys.exit(1)

    # Get the list of Fusion releases
    response = urlopen(FUSION_XML)
    fusion_xml = response.read()
    build, file_path = parse_fusion_xml(fusion_xml)

    # Download the com.vmware.fusion.zip.tar file
    print(f'Retrieving Fusion build {build} from: {file_path}')
    urlretrieve(file_path, FUSION_TAR_PATH, MyProgressBar())

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
