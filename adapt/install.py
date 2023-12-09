#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run "apt install [package]" and keep track of installed packages.
"""

from pathlib import Path
from configparser import ConfigParser
import subprocess
import argparse
from datetime import datetime

def _write_package_name(packages, file):
    """ Append `packages` (list or str) to `file` with current date and time. """
    if isinstance(packages, str):
        packages = [packages]
        
    now = datetime.now().isoformat()
    rows = [f"{now},{pkg}" for pkg in packages]
    text = "\n".join(rows)
    
    with open(file, 'a') as fileobj:
        fileobj.write(text + "\n")
        
def _remove_package_name(packages, file):
    """ Remove `packages` (list or str) from `file` """
    if not file.exists():
        return None
    
    if isinstance(packages, str):
        packages = [packages]
        
    with open(file) as fileobj:
        text = fileobj.read()
        
    rows = [row for row in text.split("\n") if row and row.split(',')[1] not in packages]
    text = "\n".join(rows)
    
    with open(file, 'w') as fileobj:
        fileobj.write(text + "\n")

def _packages_file():
    """ 
    Return Path to csv file of installed packages. 
    
    Make file and directory, along with config file pointing to it, if required.
    """
    user = Path.home()
    config_file = user.joinpath(".config", "adapt", "adapt.conf")
    config = ConfigParser()
    
    if config_file.exists():
        config.read(config_file)
        packages_file = Path(config["GENERAL"]["InstalledFilePath"])
    else:
        # make .config/adapt dir, if necessary
        config_file.parent.mkdir(parents=True, exist_ok=True)
        # make .local/share/adapt dir, if necessary
        packages_file = user.joinpath(".local", "share", "adapt", "packages.csv")
        packages_file.parent.mkdir(parents=True, exist_ok=True)
        
        config["GENERAL"] = {"InstalledFilePath":packages_file}
        with open(config_file, 'w') as fileobj:
            config.write(fileobj)
            
    return packages_file

def install(package, remove=False, purge=False):
    """ 
    Install `package` and update csv file.
    
    Parameters
    ----------
    package : {list, str}
        Name of package (or list of names) to install or remove
    remove : bool
        If True, run 'apt remove [package]'. Default is False.
    purge : bool
        If True, run 'apt remove --purge [package]'. Default is False.
    """
    packages_file = _packages_file()
    
    # install if no optional args provided
    cmd = ["apt", "install"]
    if purge:
        cmd = ["apt", "remove", "--purge"]
    elif remove:
        cmd = ["apt", "remove"]
    
    # function to call to update packages.csv
    func = _remove_package_name if remove or purge else _write_package_name
    
    # run command
    cmd = ["sudo"] + cmd + package
    proc = subprocess.run(cmd)
    rc = proc.returncode
    
    if rc == 0:
        # update pacakges.csv if command was successful
        func(package, packages_file)
    
def make_argparser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', nargs='+', help='package(s) to install')
    parser.add_argument('-r', '--remove', action='store_true',
                        help='remove package')
    parser.add_argument('-p', '--purge', action='store_true',
                        help='remove with purge')
    return parser

def main(*args):
    parser = make_argparser()
    args = parser.parse_args(args)
    install(**vars(args))
    
if __name__ == '__main__':
    import sys
    main(sys.argv[1:])