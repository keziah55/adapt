# adapt

A couple of simple Python scripts to improve `apt` user experience.

## Usage

You may wish to make `adapt.py` exectuable with, then link it to a location in 
your `PATH`, eg:
```bash
chmod 755 adapt.py
ADAPT=`readlink -f adapt.py`
cd ~/bin
ln -s $ADAPT adapt
```

### adapt install

You can use
```bash
adapt install [package]
```
to install a package (or packages) and write the package name, along with the 
current date and time, to `~/.local/share/adapt/packages.csv`. 
Packages can be removed or purged with the `-r` or `-p` optoins, respectively.

### adapt search

Search for a package with
```bash
adapt search [package]
```
If given the option `-i`, only packages that are currently installed are shown;
`-n` shows only those that are not installed. To only match the exact package 
name given, use `-e`.