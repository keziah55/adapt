#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run "apt install [package]" and keep track of installed packages.
"""

import os
from configparser import ConfigParser
import subprocess
import argparse
from datetime import datetime

def _write_package_name(packages, file):
    if isinstance(packages, str):
        packages = [packages]
        
    now = datetime.now().isoformat()
    rows = [f"{now},{pkg}\n" for pkg in packages]
    text = "".join(rows)
    
    with open(file, 'a') as fileobj:
        fileobj.write(text)
        
def _remove_package_name(packages, file):
    if not os.path.exists(file):
        return None
    
    if isinstance(packages, str):
        packages = [packages]
        
    with open(file) as fileobj:
        text = fileobj.read()
        
    rows = [row for row in text.split("\n") if row]
    rows = [f"{row}\n" for row in rows if row.split(',')[1] not in packages]
    text = "".join(rows)
    
    with open(file, 'w') as fileobj:
        fileobj.write(text)
        
def _update_package_list(file):
    proc = subprocess.run(["apt", "list"], stdout=subprocess.PIPE)
    packages = proc.stdout.decode("utf-8")
    packages = [package.split("/")[0] for package in packages]
    
    with open(file) as fileobj:
        text = fileobj.read()
        
    # make list of packages that also appear in apt list output
    rows = [row for row in text.split("\n") if row]
    rows = [f"{row}\n" for row in rows if row.split(',')[1] in packages]
    text = "".join(rows)
    
    with open(file, 'w') as fileobj:
        fileobj.write(text)
            
if __name__ == '__main__':
    
    desc = __doc__
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('package', nargs='+', help='package(s) to install')
    parser.add_argument('-r', '--remove', action='store_true',
                        help='remove package')
    parser.add_argument('-p', '--purge', action='store_true',
                        help='remove with purge')
    
    user = os.path.expanduser("~")
    configFile = f"{user}/.config/adapt/adapt.conf"
    config = ConfigParser()
    
    if os.path.exists(configFile):
        config.read(configFile)
        installedFilePath = config["GENERAL"]["InstalledFilePath"]
    else:
        os.makedirs(os.path.dirname(configFile), exist_ok=True)
        installedFilePath = f"{user}/.config/adapt/packages.csv"
        config["GENERAL"] = {"InstalledFilePath":installedFilePath}
        with open(configFile, 'w') as fileobj:
            config.write(fileobj)
            
    args = parser.parse_args()
    
    # install if no optional args provided
    cmd = ["apt", "install"]
    if args.remove:
        cmd = ["apt", "remove"]
    if args.purge:
        # 'if' here, not 'elif', in case both -r and -p provided (unnecessarily)
        cmd = ["apt", "remove", "--purge"]
        
    func = _remove_package_name if args.remove or args.purge else _write_package_name
        
    cmd = ["sudo"] + cmd + args.package
    
    proc = subprocess.run(cmd)
    rc = proc.returncode
    
    if rc == 0:
        func(args.package, installedFilePath)
    