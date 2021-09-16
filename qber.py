#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
from subprocess import call, Popen, PIPE
from sqlite3 import *


bindingsDefault = {'-collision': None, '-t': False, '-restore': False, '-self': False}

storeDefault = {'-n': None, '-t': 'auto', '-b': False, '-c': False, '-C': False, '-rm': False, '-hidden': False, '-v': False}

queryDefault = {'-a': 'all', '-t': None, '-s': None, '-c': None, '-i': None, '-e': False, '-ord': None, '-time': False, '-f': False, '-b': False, '-k': '0', '-hdr': None, '-o': None, '-bed': None, '-g': '1', '-markdup': False, '-v': False}

collideDefault = {'-d': None, '-t1': None, '-t2': None, '-s': 'all', '-j': 'inner', '-a1': None, '-a2': None, '-c': None, '-ord': None, '-rm': False, '-w': None, '-time': False, '-o': None, '-a': None, '-v': False}


def checkBindings(src):
	E = 0
	N = 1
	tmp = src + '.tmp'
	wrt = open(tmp, 'w')
	han = open(src, 'r')
	hdr = han.readline()
	dim = len(hdr.strip().split())
	wrt.write(hdr)
	
	line = han.readline().strip().split()
	
	while line != []:
		if len(line) == dim:
			wrt.write('\t'.join(line) + '\n')
		else:
			E += 1
		line = han.readline().strip().split()
		N += 1
	
	wrt.close()
	han.close()
	os.remove(src)
	os.rename(tmp, src)
	
	if E > 0:
		print('# WARNING: removed', E, 'lines over', N, '(' +\
		       str(round(100*float(E)/N, 3)) + '%)')
	else:
		print('# WARNING: no errors occurred. Input file not changed.')


def tab2db(src, table = 'auto', db = None, blob = False):
	
	if table == 'auto':
		table = os.path.basename(src).split('.')[0]
	
	if db == None:
		db = src.split('.')[0] + '.idb'
	
	han = open(src, 'r')
	hdr = han.readline().rstrip('\n').split()
	v = ('?,' * len(hdr)).strip(',')
	
	# Check data types
	
	if not blob:
		dtypes = []
		line = han.readline().rstrip('\n').split()
		for x in line:
			if isint(x):
				dtypes += ['INTEGER']
			elif isfloat(x):
				dtypes += ['REAL']
			else:
				dtypes += ['TEXT']
	else:
		dtypes = ['BLOB'] * len(hdr)
	
	han.close()
	han = open(src, 'r')
	han.readline()
	
	connection = connect(db)
	cursor = connection.cursor()
		
	# Table constructor
	
	hdr = [h.replace('.', '_') for h in hdr]
	
	cursor.execute('CREATE TABLE IF NOT EXISTS ' + table +\
		               '(' + hdr[0] + ' ' + dtypes[0] + ')');
	
	for i in range(1, len(hdr)):
		cursor.execute('ALTER TABLE ' + table + ' ADD COLUMN ' +\
			               hdr[i] + ' ' + dtypes[i])
	
	# Data importer
	
	line = han.readline().rstrip('\n').split()
	
	while line != []:
		cursor.execute('INSERT INTO ' + table +\
	                   ' VALUES(' + v + ')', line)
		line = han.readline().rstrip('\n').split()
		
	connection.commit()
	han.close()


def sqliteStore(src, idb, tab, blob = False, ctrl = False, wctrl = False, rm = False):
	if ctrl or wctrl:
		call('clear', shell=True)
		han = open(src, 'r')
		line = han.readline().strip().split()
		print("# Header:", line, "\n")
		dim = len(line)
		c = 1
		C = []
		while line != []:
			c += 1
			line = han.readline().strip().split()
			if len(line) != dim:
				print("[!] WARNING: unmatching bindings at line", c)
				print("    Number of attributes defined:", dim)
				print("      Number of attributes found:", len(line))
				if wctrl:
					raw_input("\nPress ENTER to continue\n")
				C += [c]
		if len(C) > 0:
			print("# Incoherent number of bindings found at lines:")
			print(C)
		else:
			print("# No errors found.")
		print("\n# Done.")
	else:
		if rm:
			if os.path.isdir(src):
				for x in listAllFiles(src):
					checkBindings(x)
			else:
				checkBindings(src)
		tab2db(src, tab, idb, blob)


def rmdbdup(db, table, groupby):
	connection = connect(db)
	
	with connection:
		connection.row_factory = Row
		cursor = connection.cursor()
		
		cursor.execute('DELETE FROM ' + table +\
		               ' WHERE rowid not in (SELECT min(rowid) FROM ' +\
		               table + ' GROUP BY ' + groupby + ')')


def row2dict(data, hdr, asStrings = True):
		
	D = {}
	hdr = hdr.split(', ')
	for x in data:
		x = list(x)
		if asStrings:
			for i in range(len(x)):
				if not isnumeric(x[i]):
					x[i] = str(x[i])
		D[x[0]] = {}
		for i in range(1, len(hdr)):
			D[x[0]][hdr[i]] = x[i]
	return D


def row2list(db, data, hdr, out = None, asStrings = True):
	hdr = hdr.split(', ')
	if out == None:
		out = db.split('.')[0] + '_fetched.txt'
	w = open(out, 'w')
	w.write('\t'.join(hdr) + '\n')
	for x in data:
		x = list(x)
		if asStrings:
			x = [str(x[i]) for i in range(len(x))]
		w.write('\t'.join(x) + '\n')


def db2dict(db, table, attr = 'all', cond = None, idl = None, r2d = True, verb = False):
	
	connection = connect(db)
	
	with connection:
		
		connection.row_factory = Row
		cursor = connection.cursor()
		
		if attr == 'all':
			attr = '*'
		
		if idl != None:
			# idl = <attribute_name:id_list>; e.g., SNP:snp_ids.txt
			(ian, idl) = idl.split(':')
			ian = ian + ' in ('
			
			# Query
			
			with open(idl, 'r') as han:
				for line in han:
					ian += '"' + line.strip() + '", '
			if cond != None and cond != '':
				cond = ian.strip(', ') + ') AND ' + cond
			else:
				cond = ian.strip(', ') + ')'
		if cond != None:
			if verb:
				print('#    DB: ' + db)
				print('# Query: SELECT ' + attr + ' FROM ' + table +\
				      ' WHERE ' + cond)
			cursor.execute('SELECT ' + attr + ' FROM ' + table +\
			               ' WHERE ' + cond)
		else:
			if verb:
				print('#    DB: ' + db)
				print('# Query: SELECT ' + attr + ' FROM ' + table)
			cursor.execute('SELECT ' + attr + ' FROM ' + table)
		
		# Return row/dict object
		
		rows = cursor.fetchall()
		if r2d and not attr == '*':
			return row2dict(rows, attr)
		else:
			if attr == '*':
				print('# Warning: attr parameter set to *: ' +\
				      'dictionary conversion not possible')
			return rows


def fetchData(db, table, attr = 'all', cond = None, idl = None, exclude = False, orderby = None, out = None, glist = 1, verb = False):
	
	connection = connect(db)
	
	with connection:
		
		connection.row_factory = Row
		cursor = connection.cursor()
		
		if attr == 'all':
			attr = '*'
		
		if cond == None:
			cond = ''
		else:
			cond = ' WHERE ' + cond
		
		if orderby == None:
			orderby = ''
		else:
			orderby = ' ORDER BY ' + orderby
		
		# Filtering by an ID list
		
		if idl != None:
			
			# idl = <attribute_name:id_list>; e.g., SNP:snp_ids.txt
			
			(ian, idl) = idl.split(':')
			if exclude:
				ian = ian + ' not in ('
			else:
				ian = ian + ' in ('
			
			glist -= 1
			with open(idl, 'r') as han:
				for line in han:
					if line != '\n' and not line.startswith('#') and not line.startswith('entrez'):
						ian += '"' + line.strip().split()[glist] + '", '
			if cond != '':
				cond = cond + ' AND ' + ian.strip(', ') + ')'
			else:
				cond = ' WHERE ' + ian.strip(', ') + ')'
		
		# Query
		
		if verb:
			print('#    DB: ' + db)
			print('# Query: SELECT ' + attr + ' FROM ' + table + cond +\
			      orderby)
		cursor.execute('SELECT ' + attr + ' FROM ' + table + cond +\
		               orderby)
		
		# Fetching data
		
		if out == None:
			out = db.split('.')[0] + '_fetched.txt'
		rows = cursor.fetchall()
		row2list(db, rows, attr, out)
		
		# Output report
		
		if verb:
			L = 0
			ctrl = True
			with open(out, 'r') as han:
				for line in han:
					if ctrl:
						F = len(line.strip().split())
						ctrl = False
					L += 1
			print('[!] 1 file created:', out)
			if idl != None:
				print('# Input IDs:', fileLen(idl))
			print('# Output fields:', F)
			print('# Output lines:', L-1, '(excluding header line)')


def tJoin(db, ta, tb, attr = 'all', J = 'inner', ta_attr = None, tb_attr = None, cond = None, orderby = None, out = None, verb = False):
	
	connection = connect(db)
	
	with connection:
		
		connection.row_factory = Row
		cursor = connection.cursor()
		
		if attr == 'all':
			attr = '*'
		
		if cond == None:
			cond = ''
		else:
			cond = ' WHERE ' + cond
		
		if orderby == None:
			orderby = ''
		else:
			orderby = ' ORDER BY ' + orderby
		
		if J == 'inner':
			if verb:
				print('#    DB: ' + db)
				print('# Query: SELECT ' + attr + ' FROM ' + ta +\
				      ' JOIN ' + tb + ' ON ' + ta_attr + '=' +\
				      tb_attr + cond + orderby)
			
			cursor.execute('SELECT ' + attr + ' FROM ' + ta +\
				           ' JOIN ' + tb + ' ON ' + ta_attr + '=' +\
				           tb_attr + cond + orderby)
		
		elif J == 'natural':
			if verb:
				print('#    DB: ' + db)
				print('# Query: SELECT ' + attr + ' FROM ' + ta +\
				      ' NATURAL JOIN ' + tb + cond + orderby)
			
			cursor.execute('SELECT ' + attr + ' FROM ' + ta +\
				           ' NATURAL JOIN ' + tb + cond + orderby)
		
		elif J == 'left':
			if verb:
				print('#    DB: ' + db)
				print('# Query: SELECT ' + attr + ' FROM ' + ta +\
				      ' LEFT JOIN ' + tb + ' ON ' + ta_attr + '=' +\
				      tb_attr + cond + orderby)
			
			cursor.execute('SELECT ' + attr + ' FROM ' + ta +\
				           ' LEFT JOIN ' + tb + ' ON ' + ta_attr +\
				           '=' + tb_attr + cond + orderby)
		
		# Fetching data
		
		rows = cursor.fetchall()
		row2list(db, rows, attr, out)


def dbdiff(db, table1, table2, cond = None, attr = 'all', out = None, verb = False):
	
	connection = connect(db)
	
	with connection:
		
		connection.row_factory = Row
		cursor = connection.cursor()
		
		if attr == 'all':
			attr = '*'
		
		if cond == None:
			raise IOError(': missing fields for difference')
		else:
			cond = cond.split(', ')
		
		# Query
		
		if verb:
			print('#    DB: ' + db)
			print('# Query: SELECT ' + attr + ' FROM ' + table1 +\
			      ' WHERE ' + cond[0] + ' Not IN (SELECT DISTINCT ' +\
			      cond[1] + ' FROM ' + table2 + ')')
		
		cursor.execute('SELECT ' + attr + ' FROM ' + table1 +\
		               ' WHERE ' + cond[0] + ' Not IN ' +\
		               ' (SELECT DISTINCT ' + cond[1] + ' FROM ' +\
		               table2 + ')')
		
		# Fetching data
		
		rows = cursor.fetchall()
		row2list(db, rows, attr, out)


def query(db, table, attr = 'all', cond = None, idl = None, r2d = True, verb = False):
	
	connection = connect(db)
	
	with connection:
		
		connection.row_factory = Row
		cursor = connection.cursor()
		
		if attr == 'all':
			attr = '*'
		
		if cond == None:
			cond = ''
		else:
			cond = ' WHERE ' + cond
		
		if orderby == None:
			orderby = ''
		else:
			orderby = ' ORDER BY ' + orderby
		
		if idl != None:
			# idl = <attribute_name:id_list>; e.g., SNP:snp_ids.txt
			(ian, idl) = idl.split(':')
			ian = ian + ' in ('
			
			# Query
			
			with open(idl, 'r') as han:
				for line in han:
					ian += '"' + line.strip() + '", '
			if cond != None and cond != '':
				cond = ian.strip(', ') + ') AND ' + cond
			else:
				cond = ian.strip(', ') + ')'
		
		if verb:
			print('#    DB: ' + db)
			print('# Query: SELECT ' + attr + ' FROM ' + table +\
			      ' WHERE ' + cond + orderby)
		cursor.execute('SELECT ' + attr + ' FROM ' + table +\
		               ' WHERE ' + cond + orderby)
		
		# Return row/dict object
		
		rows = cursor.fetchall()
		if r2d and not attr == '*':
			data = row2dict(rows, attr)
			print
			for k in data.keys():
				print(k + ' --> ' + str(data[k]))
		else:
			if attr == '*':
				print('# Warning: attr parameter set to *: ' +\
				      'dictionary conversion not possible')
				print
			print(rows)


def tableCheck(A, B = None, skipHeader = False, collisionCheck = False, sfx='tmp_', verbose = False):
	if B == None:
		inn = [A]
	else:
		inn = [A, B]	
	for x in inn:
		c = 1
		han = open(x, 'r')
		if skipHeader:
			han.readline()
		line = han.readline().strip().split()
		r = len(line)
		while line != []:
			line = han.readline().strip().split()
			c += 1
			t = len(line)
			if t != r and c < fileLen(x):
				print('\n[!] BindingError in file', os.path.basename(x))
				raise OSError('Incorrect number of bindings at line ' + str(c))
			else:
				r = t	
	if len(inn) == 1 and verbose:
		print('OK')
	else:
		if verbose:
			print('OK')
			print('# Checking field names collision ...',)
		err = 0
		han1 = open(A, "r")
		han2 = open(B, "r")
		H1 = han1.readline().strip().split()
		H2 = han2.readline().strip().split()
		han1.close()
		han2.close()
		c = 0; I = []
		for x in H2:
			if x in H1:
				if verbose:
					if c == 0:
						print('\n[!] field collision:', x)
					else:
						print('[!] field collision:', x)
				err += 1
				I += [c]
			c += 1
		if err > 0:
			if verbose:
				print('[!] Warning:', err, 'field collisions found.')
			for i in range(err):
				H2[I[i]] = sfx + H2[I[i]]
			rmHead(B)
			addHead(B, '\t'.join(H2))
			if verbose:
				print('[!] File', os.path.basename(B) +\
					  ': field names updated.')
		elif verbose:
			print('OK')


def restoreBindings(src, sfx = 'tmp_', verbose = True):
	res = 0
	han = open(src, 'r')
	hdr = han.readline().strip().split()
	han.close()
	for i in range(len(hdr)):
		if hdr[i].startswith(sfx):
			hdr[i] = hdr[i].replace(sfx, '')
			res += 1
	rmHead(src)
	addHead(src, '\t'.join(hdr))
	if verbose:
		if res > 1:
			print('[!] Restored', res, 'fields.')
		elif res == 1:
			print('[!] Restored 1 field.')
		else:
			print('[!] No fields to be restored.')


def hawks(src, red = None, srt = None, sep = '\t', unique = False, rev = False, out = None):
	
	CML = ''
	
	if out == None:
		out = src.split('.')[0] + '_filtered.txt'
	
	if rev:
		rev = ' -r'
	else:
		rev = ''
	
	if red == None and srt == None:
		raise SyntaxError('invalid operation')
	
	if srt != None:
		CML += 'sort' + rev + ' -t "' + sep + '" ' +\
		       srt.replace('x', '-k') + ' ' + src
		if red != None:
			CML += ' | '
			inn = ''
		else:
			call(CML + ' > ' + out, shell=True)
			if unique and os.path.isfile(out):
				unique(out)
			return 0
	else:
		inn =  ' ' + src
	
	if red != None:
		CML += 'awk -v OFS=\"' + sep + '\" \'{print ' +\
		       red.replace('x', '$').replace(' ', ',') + '}\'' + inn +\
		       ' > ' + out
		call(CML, shell=True)
		if unique and os.path.isfile(out):
			unique(out)
		return 1


def sortBed(src, rev = False, warn = True, fileCheck = True):
	
	try:
		if os.path.isfile(src):
			inn = [src]
		elif os.path.isdir(src):
			inn = listAllFiles(src)
	except:
		if warn:
			print('# WARNING: input file or directory not found!')
	
	for x in inn:
		tmp = x.split('.')[0] + '_tmp_sorted.bed'
		if fileCheck and checkBedHeader(x):
				B, H = splitHead(src)
				os.remove(x)
				os.rename(B, x)
		else:
			H = None
		if rev:
			call('sort -k1,1 -k2,2nr ' + x + ' > ' + tmp, shell=True)
		else:
			call('sort -k1,1 -k2,2n ' + x + ' > ' + tmp, shell=True)
		os.remove(x)
		os.rename(tmp, x)
		if fileCheck and H not in (None, ''):
			call("sed -i -e '1i" + H + "\' " + x, shell = True)
	return src


def addHead(src, hdr):
	tmp = src.split('.')[0] + '_addHead.tmp'
	hdr = '\t'.join(hdr.split()) + '\n'
	wrt = open(tmp, 'w')
	wrt.write(hdr)
	with open(src, 'r') as han:
		for line in han:
			wrt.write(line)
	wrt.close()
	os.remove(src)
	os.rename(tmp, src)
	return src


def rmHead(src):
	tmp = src.split('.')[0] + '_rmhead.tmp'
	call('tail -n +2 ' + src + ' > ' + tmp, shell=True)
	os.remove(src)
	os.rename(tmp, src)
	return src


def splitHead(src):
	if fileLength(src) > 0:
		ctrl = True
		w = open(src + '.body', 'w')
		with open(src, 'r') as han:
			for line in han:
				if ctrl:
					hdr = line
					ctrl = False
				else:
					w.write(line)
		w.close()
		return (src + '.body', hdr)
	else:
		copyfile(src, src + '.body')
		return (src + '.body', '')


def unique(src):
	tmp = src + '.tmp'
	call('awk \'!seen[$0]++\' ' + src + ' > ' + tmp, shell = True)
	os.remove(src)
	os.rename(tmp, src)


def isint(x):
	try:
		a = float(x)
		b = int(a)
	except ValueError:
		return False
	else:
		return a == b


def isfloat(x):
	try:
		a = float(x)
	except ValueError:
		return False
	else:
		return True


def fileLen(src):
	try:
		with open(src) as f:
			for i, N in enumerate(f):
				pass
		return i + 1
	except:
		return 0


def fileLength(src):
	call('wc -l ' + src + ' > flength_tmp.txt', shell=True)
	han = open('flength_tmp.txt', 'r')
	n = int(han.readline().split()[0])
	han.close()
	os.remove('flength_tmp.txt')
	return n


def readOp(args, defaultVals=None):
	Op = {}
	for i in range(len(args)):
		try:
			if args[i].startswith('-') and (isint(args[i+1]) or\
			   isfloat(args[i+1]) or not args[i+1].startswith('-')):
				Op[args[i]] = args[i+1]
			elif args[i].startswith('-'):
				Op[args[i]] = True
		except:
			if args[i].startswith('-'):
				Op[args[i]] = True
	if defaultVals != None:
		for K in Op.keys():
			defaultVals[K] = Op[K]
	else:
		defaultVals = Op
	return defaultVals
