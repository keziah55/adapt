# adapt

A couple of simple Python scripts to improve `apt` user experience.

## Dependencies

The are no required dependencies, beyond Python >= 3.8, however you may wish
to install `python3-xtermcolor` to enable colored output from `adapt search`.

## Usage

You may wish to make `adapt.py` exectuable, then link it to a location in 
your `PATH`, eg:
```bash
chmod 755 adapt.py
ADAPT=`readlink -f adapt.py`
cd ~/.local/bin
ln -s $ADAPT adapt
```

The following sections assume you have done this, or something similar, and so 
you can simply call `adapt` rather than `python3 adapt.py`

### adapt install

`adapt install` runs `sudo apt install` internally.

To install a package (or packages), use
```bash
adapt install [package]
```
This automatically logs the package name, along with the current date and time, 
in `~/.local/share/adapt/packages.csv`. 

Packages can be removed or purged with the `-r` or `-p` options, respectively.

See `adapt install -h` for all options.

### adapt search

`adapt search` runs `apt search` internally.

To search for a package, use
```bash
adapt search [package]
```

If given the option `-i`, only packages that are currently installed are shown;
`-n` shows only those that are not installed. To only match the exact package 
name given, use `-e`.

See `adapt search -h` for all options.