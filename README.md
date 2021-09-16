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
If the input is a file, a single index will be created.
If the input is a directory, every file will be stored in the index database as a table.

```
kew.py store <input> [options]

# OPTIONS
# -n  A database name. If None (default), the input file name with .idb extension will be used.
```
