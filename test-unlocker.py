#!/usr/bin/env python

import shutil
import unlocker


def main():
    # Test Windows patching
    print('Windows Workstation 16')
    shutil.copyfile('./samples/windows/vmware-vmx.exe', './tests/windows/vmware-vmx.exe')
    unlocker.patchsmc('./tests/windows/vmware-vmx.exe', False)
    shutil.copyfile('./samples/windows/vmwarebase.dll', './tests/windows/vmwarebase.dll')
    unlocker.patchbase('./tests/windows/vmwarebase.dll')

    # Test Linux patching
    print('Linux Workstation 16')
    shutil.copyfile('./samples/linux/vmware-vmx', './tests/linux/vmware-vmx')
    unlocker.patchsmc('./tests/linux/vmware-vmx', True)
    shutil.copyfile('./samples/linux/libvmwarebase.so', './tests/linux/libvmwarebase.so')
    unlocker.patchbase('./tests/linux/libvmwarebase.so')

    # Test macOS patching
    print('macOS Fusion 12')
    shutil.copyfile('./samples/macos/vmware-vmx', './tests/macos/vmware-vmx')
    unlocker.patchsmc('./tests/macos/vmware-vmx', False)

    # Test ESXi patching
    print('ESXi 7.0')
    shutil.copyfile('./samples/esxi/vmx', './tests/esxi/vmx')
    unlocker.patchsmc('./tests/esxi/vmx', True)
    shutil.copyfile('./samples/esxi/libvmkctl.so', './tests/esxi/libvmkctl.so')
    unlocker.patchvmkctl('./tests/esxi/libvmkctl.so')


if __name__ == '__main__':
    main()
