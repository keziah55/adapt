#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run "apt search [package]", optinally showing only those packages which are
either installed (-i) or not installed (-n).
"""

import subprocess
import argparse
import re
try:
    from xtermcolor import colorize
except ImportError:
    print("Install python3-xtermcolor for fancier output formatting")
    colorize = None

def filter_search(text, installed=True, match_exact=None):
    """ 
    Take text from apt search command, filter and print.
    
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
    lines = _join_items(lines)
    
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
            
def _print_colour(line):
    """ Print with colour, as apt search does. """
    
    line = line.split('/')
    # package name (up to first slash) green...
    name = line[0]
    # ...rest normal
    rest = '/' + '/'.join(line[1:])
    
    if colorize is not None:
        # for bright green, ansi=46
        print_args = [colorize(name, ansi=2)]
    else:
        print_args = [name]
    print_args += [rest, '\n']
        
    print(*print_args)
                
def _check_line(line, pattern, filter_in, mode='any'):
    """ 
    Check if `pattern` is or is not in `line`
    
    Parameters
    ----------
    line : str
        string to check
    pattern : str or list
        string, or list of strings, to look for
    filter_in : bool
        If True, return True if pattern in line, else return False.
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
    
    if filter_in:
        return func([p in line for p in pattern])
        
    if not filter_in:
        return func([p not in line for p in pattern])
            
def _filter_non_results(line):
    """ Return False if `line` should be filtered out of output. Otherwise, return True. """
    # False if empty line
    if not line.strip():
        return False
    # False if opening apt search lines
    elif re.match('Sorting...', line):
        return False
    elif re.match('Full Text Search...', line):
        return False
    else:
        return True
    
def _join_items(lst):
    """
    Given list of 'apt search' output (`lst`), group lines together for each 
    search result, i.e. package name and description.
    
    """
    # each entry is formatted thus:
    # name/distro and other info
    #   description
    
    new = []
    
    # get indices of lines that do not begin with whitespace (i.e. a new result)
    idx = [i for i, item in enumerate(lst) if re.match('\S', item)]
    idx.append(len(lst))
    
    # join together results and descriptions
    for n in range(len(idx)-1):
        new.append('\n'.join(lst[idx[n]:idx[n+1]]))
        
    return new

def main(package, installed=False, notinstalled=False, exact=False):
    """ 
    Run `apt search [package]`
    
    Parameters
    ----------
    installed : bool, optional
        If True, only show packages that are already installed. 
        Default is False.
    notinstaled : bool, optional
        If True, only show packages that are not currently installed. 
        Default is False.
    exact : bool, optional
        If True, only show packages that exactly match the given search string.
        Default is False.
    """
    
    if installed and notinstalled:
        msg = "Please select either 'installed', 'notinstalled' or neither, not both."
        raise ValueError(msg)
        
    if not installed and not notinstalled:
        installed = None
    
    if installed:
        installed = True
    elif notinstalled:
        installed = False
        
    match_exact = package if exact else None
    
    ret = subprocess.run(["apt", "search", package], 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    acs = ret.stdout.decode("utf-8")
    filter_search(acs, installed=installed, match_exact=match_exact)
    
def make_argparser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', help='search term')
    parser.add_argument('-i', '--installed', action='store_true',
                        help='return results where packages are installed')
    parser.add_argument('-n', '--notinstalled', action='store_true',
                        help='return results where packages are not installed')
    parser.add_argument('-e', '--exact', action='store_true', default=False,
                        help='only return results where the given string exactly matches the package name')
    return parser

if __name__ == '__main__':
    parser = make_argparser()
    args = parser.parse_args()
    main(**vars(args))