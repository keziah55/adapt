#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run "apt search [package]", optinally showing only those packages which are
either installed (-i) or not installed (-n).
"""

import subprocess
import argparse
import sys
import re
from xtermcolor import colorize

def filter_search(text, installed=True, match_exact=None):
    """ Take text from apt search command, filter and print.
    
        Parameters
        ----------
        text : str
            apt search command output
        installed : bool or None
            if True, only display packages which are installed. 
            If False, only display packages which are not installed.
            If None, print `text` unfiltered.
        match_exact : str or None
            If a package name is given, only results that exactly match that
            package name will be printed.
    """
    
    lines = text.split('\n')
    
    # remove lines that aren't search results
    lines = list(filter(_filter_non_results, lines))
    
    # join name and description into single list element
    lines = _join(lines)
    
    for line in lines:
        if match_exact is None or re.match(f"{match_exact}\/", line) is not None:
            if installed is None:
                # unaltered behaviour
                _print_colour(line)
            else:
                # check if 'installed' is/is not present
                check = _check_line(line, ['installed', 'upgradable'], installed)
                if check:
                    _print_colour(line)
            
            
def _print_colour(s):
    # print with colour, as apt search does
    
    l = s.split('/')
    # package name (up to first slash) green...
    name = l[0]
    # ...rest normal
    rest = '/' + '/'.join(l[1:])
    
    # for bright green, ansi=46
    print(colorize(name, ansi=2), rest, '\n')# colorize(rest, ansi=7), '\n')
                
                
def _check_line(line, pattern, bl, mode='any'):
    """ Check if `pattern` is or is not in `line`
    
        Parameters
        ----------
        line : str
            string to check
        pattern : str or list
            string, or list of strings, to look for
        bl : bool
            if True, return True if pattern in line, else return False.
            If False, return True if pattern not in line, else return False.
        mode : {'any', 'all'}
            If given list of strings, check either if any patterns are in `line`
            or all patterns are in `line`. Default is 'any'.
            
        Returns
        -------
        bool
    """
    if isinstance(pattern, str):
        pattern = [pattern]
    
    if mode not in ['any', 'all']:
        return ValueError("mode must be 'any' or 'all'")
    
    func = any if mode == 'any' else all
    
    if bl:
        return func([p in line for p in pattern])
        
    if not bl:
        return func([p not in line for p in pattern])

            
def _filter_non_results(s):
    
    # False if empty line
    if not s.strip():
        return False
    # False if opening apt search lines
    elif re.match('Sorting...', s):
        return False
    elif re.match('Full Text Search...', s):
        return False
    else:
        return True
    
    
def _join(lst):
    # join list elements together to make, so each element is a full apt search
    # entry 
    
    # each entry is formatted thus:
    # name/distro and other info
    #   description
    # so join line which begins with whitespace with all following lines that 
    # do not
    
    new = []
    
    idx = [i for i, item in enumerate(lst) if re.match('\S', item)]
    
    idx.append(len(lst))
    
    for n in range(len(idx)-1):
        new.append('\n'.join(lst[idx[n]:idx[n+1]]))
        
    return new
        

if __name__ == '__main__':
    
    desc = __doc__
        
    parser = argparse.ArgumentParser(description=desc)
    
    parser.add_argument('package', help='search term')
    
    parser.add_argument('-i', '--installed', action='store_true',
                        help='return results where packages are installed')
    parser.add_argument('-n', '--notinstalled', action='store_true',
                        help='return results where packages are not installed')
    parser.add_argument('-e', '--exact', action='store_true', default=False,
                        help='only return results where the given string exactly matches the package name')
    
    args = parser.parse_args()
    
    if args.installed and args.notinstalled:
        raise ValueError('Please select either installed, not installed or '
                         'neither, not both.')
        sys.exit(1)
        
    if not args.installed and not args.notinstalled:
        installed = None
    
    if args.installed:
        installed = True
    elif args.notinstalled:
        installed = False
        
    match_exact = args.package if args.exact else None
    
    ret = subprocess.run(["apt", "search", args.package], 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    acs = ret.stdout.decode("utf-8")
    filter_search(acs, installed=installed, match_exact=match_exact)
    