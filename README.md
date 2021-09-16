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

## Quick guide

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

### Manual input file check
Function: `bindings`

Check input file or directory integrity. Without optional arguments, it will check the coherence between arrtibute fields and data (bindings).
An incorrect number of bindings is ofted due to spaces or special characters either within attribute names or data.

```
# NORMAL USAGE:
kew.py bindings <input_TXT> [-collision <2nd_input_TXT>] [-t]

# FIELD NAME COLLISION CHECK:
kew.py bindings <input_TXT> -self

# OPTIONS
# -self       enable attribute name collision check within the same file.
# -collision  enable attribute name collision check with a second text file.
# -t          skip the first line of the file(s).
```

### Fetch data in a text file
Function: `fetch`

Build a query and fetch data in a tab-separated text file. The input can be either a text file or an SQLite index.

```
# USAGE WITH TXT FILE
kew.py fetch <input> -f [-s <attributes>] [-c <condition>] [-i <ID_attribute>:<ID_list_file>] [options]

# USAGE WITH SQLite INDEX
kew.py fetch <input_idb> -t <table> [-s <attributes>] [-c <condition>] [-i <ID_attribute>:<ID_list_file>] [options]

# OPTIONS
# -t     Database table to be queried.
# -s     Comma + space-separated table attributes to be returned (-s "attr1, attr2, ..., attrN").
# -c     Condition on tuples (-c "...").
# -i     An attribute:ID_list string (table_attribute:ID_list_file).
#        The ID list should be given as a text file with only one ID per line.
#        If ID_list_file is a directory, a recursive query will be performed.
#        Every output file of the recursive query will have .map extension.
# -ord   Comma + space-separated table attributes to order by (-ord "attr1, attr2, ..., attrN").
#        This will sort data according to the specified attributes, in ascending order.
#        For descending order, write DESC after the parameter argument (-ord "attr1, attr2, ..., attrN DESC").
# -o     Output path. If None, the output will be set automatically to basename(<index_db>)_fetched.txt
# -e     Exclude IDs in -i. Use with -i only.
# -f     Disable warnings (for automatic usage).
#        Use this option if the input is a tab-separated txt file, instead of an SQlite index.
# -time  Show elapsed time.
# -v     Suppress display output.
```
