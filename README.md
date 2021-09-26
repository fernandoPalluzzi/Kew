# Kew
**Kew** is a simple command line tool for [**SQLite**](https://sqlite.org) database creation and querying. Large datasets are often stored as big text files or directories containing many big files (e.g., more than 1 or 2GB per file). These files often come as CSV (comma or semicolon separated) format or TAB-separated text. Opening these files in text editors and/or spreadsheets could be unfeasible or impractical for many reasons, including limited resources, huge computational demands, limited number of data entries that can be processed simultaneously, complex operations (such as table joins or complex SQL clauses) that can be done only by SQL experts. **Kew** enables the creation and manipulation of big files and directories, also for non SQL or Python experts, by indexing them with the sqlite3 Python library.

## Installation

Clone the Kew repository within your favourite directory and modify the .bashrc file by adding the Kew location within the PATH variable:

```
# Extended PATH variables set
export PATH=$PATH:~/your_favourite_dir/KewTools
```

Be sure to have execution rights for the Kew directory. If not, you may change them with:

```
chmod 700 ~/your_favourite_dir/KewTools/*
```

Open a terminal and launch `kew.py` to view the current version.

## Quick guide

Use `kew.py <FUNCTION> -h` to get help.

The list of available functions (see below) can be displayed simply with `kew.py`.

### Create an SQLite database
Function: `store`

Store tab-separated (or blank-separated) txt files into an SQLite database.
If the input is a file path, a single index will be created.
If the input is a directory path, every included file will be stored in the index database as a table.

```
kew.py store <input> [options]

# ARGUMENTS
# -n       A database name. If None (default), the input file name with .idb extension will be used.
# -t       Table name. If "auto" (default), the input file basename without extension will be used.
# -b       Blob type will be used as attribute type for every attribute.
# -c       Perform a data check.
# -C       Perform an interactive data check.
# -rm      Filter out binding errors from the input file(s).
# -v       Suppress display output.
# -hidden  Enable silent mode.
```

### Manual input file check
Function: `bindings`

Check input file or directory integrity. Without optional arguments, it will check the coherence between arrtibute fields and data (bindings).
An incorrect number of bindings is ofted due to spaces or special characters either within attribute names or data.

```
# NORMAL USAGE
kew.py bindings <input_TXT> [-collision <2nd_input_TXT>] [-t]

# FIELD NAME COLLISION CHECK
kew.py bindings <input_TXT> -self

# OPTIONS
# -self       enable attribute name collision check within the same file.
# -collision  enable attribute name collision check with a second text file.
# -t          skip the first line of the file(s).
```

### Fetch data in a text file
Function: `fetch`

Build a query and fetch data in a tab-separated text file. The input can be either a text file or an SQLite database.

```
# USAGE WITH TEXT FILE
kew.py fetch <input> -f [-s <attributes>] [-c <condition>] [options]

# USAGE WITH SQLite DB
kew.py fetch <input.idb> -t <table> [-s <attributes>] [-c <condition>] [options]

# ARGUMENTS
# -t     Database table to be queried.
# -s     Comma + space-separated table attributes to be returned (-s "attr1, attr2, ..., attrN").
# -c     Condition on tuples (-c "...").
# -i     An attribute:ID_list string (attribute:ID_list_file).
#        The ID list should be given as a text file with only one ID per line.
#        If ID_list_file is a directory, a recursive query will be performed.
#        Every output file of the recursive query will have .map extension.
# -ord   Comma + space-separated table attributes to order by (-ord "attr1, attr2, ..., attrN").
#        This will sort data according to the specified attributes, in ascending order.
#        For descending order, write DESC after the parameter argument
#        (-ord "attr1, attr2, ..., attrN DESC").
# -o     Output path. If None, the output will be set automatically to 
#        basename(<index_db>)_fetched.txt
# -e     Exclude IDs in -i. Use with -i only.
# -f     Disable warnings (for automatic usage).
#        Use this option if the input is a tab-separated txt file, instead of an SQlite database.
# -time  Show elapsed time.
# -v     Suppress display output.
```

### Join between tables of a database
Function: `join`

```
kew.py join -d <input.idb> -t1 <table_1> -t2 <table_2> [-a1] [-a2] [-s <attributes>] [options]

# ARGUMENTS
# -d     SQLite database file generated by the "store" function.
# -t1    Input table 1.
# -t2    Input table 2.
# -a1    Join attribute from table 1. Not needed if -j is set to "natural" (see below).
# -a2    Join attribute from table 2. Not needed if -j is set to "natural" (see below).
# -s     Attributes to be selected (-s "attr1, attr2, ..., attrN").
# -c     Condition on tuples (-c "...").
# -j     Join type among "left", "inner", or "natural".
# -ord   Comma + space-separated table attributes to order by (-ord "attr1, attr2, ..., attrN").
#        This will sort data according to the specified attributes, in ascending order.
#        For descending order, write DESC after the parameter argument
#        (-ord "attr1, attr2, ..., attrN DESC").
# -o     Output path. If None, the output will be set automatically to
#        basename(<index_db>)_fetched.txt
# -v     Suppress display output.
# -time  Show elapsed time.
```

### Join between text files
Function: `collide`

```
kew.py collide -t1 <TXT_file_1> -t2 <TXT_file_2> [-a1] [-a2] [-a] [-s <attributes>] [options]

# ARGUMENTS
# -d     Index file generated by the "store" function.
# -t1    Input file 1.
# -t2    Input file 2.
# -a1    Join attribute from file 1. Not needed if -a is used or -j is set to "natural" (see below).
# -a2    Join attribute from file 2. Not needed if -a is used or -j is set to "natural" (see below).
# -a     If the joining attributes from both tables have the same name, the user may indicate them 
#        at once with -a.
# -s     Attributes to be selected (-s "attr1, attr2, ..., attrN").
#        The user can specify "_t1" for the entire attribute set of file_1, and "_t2" for the entire 
#        attribute set of file_2 (e.g., -s "_t1, file2_attr1, file2_attr2, ...",
#                                       -s "file1_attr1, file1_attr2, ..., _t2", or
#                                       -s "_t1, _t2")
# -c     Condition on tuples (-c "...").
# -j     Join type among "left", "inner", or "natural".
# -ord   Comma + space-separated table attributes to order by (-ord "attr1, attr2, ..., attrN").
#        This will sort data according to the specified attributes, in ascending order.
#        For descending order, write DESC after the parameter argument
#        (-ord "attr1, attr2, ..., attrN DESC").
# -o     Output path. If None, the output will be set automatically to
#        basename(<index_db>)_fetched.txt
# -rm    Remove the intermediate index database.
# -v     Suppress display output.
# -time  Show elapsed time.
```

### Remove duplicates from a database or text file
Function: `rmdup`

```
# USAGE WITH A TEXT FILE
kew.py rmdup <input_file> < -b | -f > -s <groupby> [options]

# USAGE WITH AN SQLite INDEX
kew.py rmdup <input.idb> -t <table> -s <groupby> [options]

# ARGUMENTS
# <input>   Either a tab or blank separated txt file or an SQLite index generated by "store".
# -t        Table to be cleaned. If the input is a file, -t is not required.
# -s        Attribute(s) to be considered as a unique key.
#           Only the first among a group of tuples with the same key is retained.
# -b        Use this option if you want a backup copy (.bkp) of the input file
#           (not an SQLite index database).
# -f        Use this option if the input is a file (not an SQLite index database).
#           Differently from -b, the output will replace the input file.
# -bed      Use this option if the input is a BED file (not a .idb file) and you want a sorted 
#           output file.
# -c        Condition on tuples (-c "...").
# -i        An attribute:ID_list string (table_attribute:ID_list_file).
#           The ID list should be given as a text file with only one ID per line.
#           If ID_list_file is a directory, a recursive query will be performed.
#           Every output file of the recursive query will have .map extension.
# -k        Fields used to sort data. By default, the "rmdup" function retains the
#           first occurrence of a duplicated key. Sorting will decide which line 
#           will appear first. This option will sort the input file before processing it
#           (see also -ord option below).
#           In the sorting argument, each column in the input file is represented 
#           with an "x" followed by a number, indicating the start and the end position
#           of the chosen fields. For example, -k "x4,4" sorts the file by column 4 
#           (i.e. the key starts in column 4 and ends in column 4).
#           To sort a BED file by chromosome and then by start the option will be:
#           -k "x1,1 x2,2n" (chromosome is column 1 and start is column 2).
#           The sorting argument has the following general sintax:
#             -k "xFIELD,FIELD[OPT] x..."
#           where FIELD is a column number, and OPT sort by an option, following
#           Bash sort function:
#                                b  ignore leading blanks
#                                d  consider only blanks and alphanumeric characters
#                                f  ignore case
#                                g  general numeric sort
#                                i  ignore non-printable characters
#                                M  month sort
#                                h  human-readable sort (e.g. 2K, 1G)
#                                n  numbers are considered numeric strings
#                                R  random sort
#                                r  reverse order
#                                V  natural sort of version numbers within text
# -ord      Comma + space-separated table attributes to order by (-ord "attr1, attr2, ..., attrN").
#           This will sort data according to the specified attributes, in ascending order.
#           For descending order, write DESC after the parameter argument
#           (-ord "attr1, attr2, ..., attrN DESC").
#           Differently from -k option (see above), -ord will sort only the output.
# -hdr      Header to be added to the input file.
#           Header format must be a comma + space separated list of attribute names
#           (<attr1, attr2, ...>).
#           Use this option if -b or -f are enabled and the input file has no header.
# -markdup  Duplicate entries in the i-th field are marked instad of removed.
#           A "duplicates" field will be added to the output file. 
# -v        Suppress display output.
```

### Difference between tables
Function: `difference`

Find all values for the selected *attributes* from *table1* and *table2* for which *field1* (from *table1*) has no values in common with *field2* (from *table2*).

```
kew.py difference <input.idb> -t1 <table1> -t2 <table2> -w <field1, field2> -a <attributes> [-v]

# ARGUMENTS
# -t1    Input table 1.
# -t2    Input table 2.
# -w     Field pair used for the comparison (-w "attribute1, attribute2").
# -a     Selected attributes.
# -time  Show elapsed time.
# -v     Suppress display output.
```
