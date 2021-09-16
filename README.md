# Kew
**Kew** is a simple command line tool for SQLite indexes creation and querying.

## Installation

Clone the Kew repository within the home directory and modify the .bashrc file by adding Kew within the PYTHONPATH variable:

```
# Extended PATH variables set
export PYTHONPATH=$PYTHONPATH:~/Kew
```

Be sure to have execution rights for the Kew directory. If not, you may change them with:

```
chmod 700 ~/Kew
```

## Quickstart

### Create an SQLite index
Function: `store`

Store tab-separated (or blank-separated) txt files into an SQLite database.
If the input is a file path, a single index will be created.
If the input is a directory path, every included file will be stored in the index database as a table.

```
kew.py store <input> [options]

# OPTIONS
# -n  A database name. If None (default), the input file name with .idb extension will be used.
# -t  Table name. If "auto" (default), the input file basename without extension will be used.
# -b  Blob type will be used as attribute type for every attribute.
# -c  Perform a data check.
# -C  Perform an interactive data check.
# -rm      Filter out binding errors from the input file(s).
# -v       Suppress display output.
# -hidden  Enable silent mode.
```
