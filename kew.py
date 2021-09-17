#! /usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import time
from subprocess import call, Popen, PIPE
from shutil import copyfile
from qber import *


if len(sys.argv) == 1 or sys.argv[1] == "version":
	call('clear', shell = True)
	print('\n  ##### The Kew Toolkit v0.1.1b    (c) 2021 Fernando Palluzzi #####\n')
	print('  ## Use "kew.py <FUNCTION> -h" for help ##\n')
	print('  o~~~~~~~~~~~~~o~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~o')
	print('  | Function    |  Description                                    |\n' +
	      '  o-------------o-------------------------------------------------o\n' +
	      '  | store       |  Create an SQLite index                         |\n' +
	      '  | bindings    |  Manual input file check                        |\n' +
	      '  | fetch       |  Fetch data in a text file                      |\n' +
	      '  | join        |  Join between tables of a database              |\n' +
	      '  | collide     |  Join between text files                        |\n' +
	      '  | rmdup       |  Remove duplicates from a database or text file |\n' +
	      '  | difference  |  Difference between tables                      |')
	print('  o~~~~~~~~~~~~~o~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~o\n')

elif sys.argv[2] == "-h":
	call('clear', shell = True)
	print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
	call('cat ~/KewTools/manual/' + sys.argv[1] + '.txt', shell = True)
	print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')


elif sys.argv[1] == "store":
	Op = readOp(sys.argv, storeDefault)
	
	if Op['-n'] == None:
		Op['-n'] = sys.argv[2].split('.')[0] + '.idb'
	
	if not Op['-v']:
		print('# Storing input data in ' + Op['-n'] + ' ...')
	elif Op['-hidden']:
		print('# Storing input data ...')

	if os.path.isfile(sys.argv[2]):
		sqliteStore(sys.argv[2], Op['-n'], Op['-t'], Op['-b'], Op['-c'],
		            Op['-C'], Op['-rm'])
	
	elif os.path.isdir(sys.argv[2]):
		for x in listAllFiles(sys.argv[2]):
			print('# Indexing file', x, '...')
			sqliteStore(x, Op['-n'], Op['-t'], Op['-b'], Op['-c'],
			            Op['-C'], Op['-rm'])
	
	else:
		raise OSError(sys.argv[2] + ': no such file or directory')
	
	if not Op['-v'] or Op['-hidden']:
		print('# Done.')


elif sys.argv[1] == "rmdup":	
	Op = readOp(sys.argv, queryDefault)
	
	if not Op['-v']:
		if Op['-markdup']:
			print('# Marking duplicates in ' + sys.argv[2] + ' ...')
		else:
			print('# Removing duplicates from ' + sys.argv[2] + ' ...')
	
	if Op['-b']:
		copyfile(sys.argv[2], sys.argv[2] + '.bkp')
		if not Op['-markdup']:
			Op['-f'] = True
	
	if Op['-f']:
		L0 = fileLen(sys.argv[2])
		tmp = sys.argv[2] + '.tmp'
		idb = sys.argv[2].split('.')[0] + '.idb'
		tab = os.path.basename(sys.argv[2]).split('.')[0]
		if Op['-hdr'] == None:
			B, hdr = splitHead(sys.argv[2])
			hdr = hdr.strip().replace('\t', ' ')
			H = hdr.replace(' ', ', ')
			os.remove(sys.argv[2])
			os.rename(B, sys.argv[2])
		else:
			hdr = Op['-hdr'].replace(', ', ' ')
			H = Op['-hdr']
		if str(Op['-k']) != '0':
			hawks(sys.argv[2], srt = Op['-k'], out = tmp)
			os.remove(sys.argv[2])
			os.rename(tmp, sys.argv[2])
		addHead(sys.argv[2], hdr)
		sqliteStore(sys.argv[2], idb, tab)
		rmdbdup(idb, tab, Op['-s'])
		fetchData(idb, tab, H, Op['-c'], Op['-i'], orderby = Op['-ord'],
		          out = tmp, verb = False)
		os.remove(idb)
		os.remove(sys.argv[2])
		os.rename(tmp, sys.argv[2])
		L = fileLen(sys.argv[2])
		if not Op['-v']:
			print('# Data reduction: ' + str(L) + '/' + str(L0) +\
			      ' (' + str(round(100*float(L)/L0, 3)) + '%)')
	else:
		if Op['-markdup']:
			tmp = sys.argv[2] + '.tmp'
			j = int(Op['-i']) - 1
			#f = fileLen(sys.argv[2])
			ctrl = 0
			n = 1
			if os.path.exists(sys.argv[2]):
				wrt = open(tmp, 'w')
			with open(sys.argv[2], 'r') as han:
				for line in han:
					line = line.strip().split()
					if ctrl == 0:
						wrt.write('\t'.join(line) + '\t' + line[j] +\
						          '_duplicates\n')
						ctrl += 1
					elif ctrl == 1:
						J0 = line[j]
						L = [line]
						ctrl += 1
					else:
						if line[j] == J0:
							L += [line]
							n += 1
						else:
							for x in L:
								wrt.write('\t'.join(x) + '\t' +\
								          str(n) + '\n')
							J0 = line[j]
							L = [line]
							n = 1
			wrt.close()
			os.remove(sys.argv[2])
			os.rename(tmp, sys.argv[2])
			if not Op['-v']:
				print('[!] 1 file updated:', sys.argv[2])
		else:
			rmdbdup(sys.argv[2], Op['-t'], Op['-s'])
	
	if Op['-bed']:
		sortBed(sys.argv[2])
	
	if not Op['-v']:
		if Op['-b']:
			print('[!] 1 bakup file generated:', sys.argv[2] + '.bkp')
		print('# Done.')


elif sys.argv[1] == "fetch":	
	Op = readOp(sys.argv, queryDefault)
	
	print('# Input processing. Please, wait ...')
	
	if Op['-time']:
		start_time = time.time()
	
	if os.path.exists(sys.argv[2]):
		if sys.argv[2].split('.')[1] != 'idb':
			if Op['-f']:
				ctrl = True
			else:
				print('[!] WARNING: input file extension is not .idb')
				ans = raw_input('[!] Is ' +\
				                os.path.basename(sys.argv[2]) +\
				                ' an SQLite database?\n    ' +\
				                '(y: yes; n: no; c: abort)' +\
				                '\n------------------------------' +\
				                '--------------------------------\n')
				if ans in ('n', 'N', 'no', 'NO'):
					ctrl = True
				elif ans in ('c', 'C', 'cancel'):
					print('# All processes terminated.')
					exit()
				else:
					ctrl = False
			if ctrl:
				call('kew.py store ' + sys.argv[2], shell = True)
				Op['-t'] = os.path.basename(sys.argv[2]).split('.')[0]
				src = sys.argv[2].split('.')[0] + '.idb'
			else:
				src = sys.argv[2]
		else:
			src = sys.argv[2]
			ctrl = False
	else:
		raise OSError(sys.argv[2] + ': file not found')
	
	if Op['-i'] == None or os.path.isfile(Op['-i'].split(':')[1]):
		if Op['-s'] == None:
			if sys.argv[2].split('.')[1] == 'idb':
				Op['-s'] = 'all'
			else:
				with open(sys.argv[2], 'r') as han:
					Op['-s'] = han.readline().strip().replace('\t', ', ')
		fetchData(src, Op['-t'], Op['-s'], Op['-c'], Op['-i'], Op['-e'],
		               Op['-ord'], Op['-o'], int(Op['-g']),
		               not(Op['-v']))
		if ctrl:
			os.remove(src)
	
	elif os.path.isdir(Op['-i'].split(':')[1]):
		for x in listAllFiles(Op['-i'].split(':')[1]):
			if Op['-s'] == None:
				with open(x, 'r') as han:
					Op['-s'] = han.readline().strip().replace('\t', ', ')
			out = os.path.join('./', os.path.basename(x)) + '.map'
			idl = Op['-i'].split(':')[0] + ':' + x
			fetchData(src, Op['-t'], Op['-s'], Op['-c'], idl, Op['-e'],
			               Op['-ord'], out, int(Op['-g']),
			               not(Op['-v']))
			if ctrl:
				os.remove(src)
		
	else:
		raise ValueError('ID list not found')
	
	if Op['-time']:
		print('# Time elapsed: ' + str(time.time() - start_time) +\
		      ' sec')
	
	if not Op['-v']:
		print('# Done.')


elif sys.argv[1] == "bindings":	
	Op = readOp(sys.argv, bindingsDefault)
	
	if Op['-restore']:
		print('# Restoring field names ...')
	
		restoreBindings(sys.argv[2], 'tmp_')
	
	if Op['-self']:
		print('# Checking field name collisions ...')
	
		han = open(sys.argv[2], 'r')
		hdr = han.readline()
		han.close()
		hdr = hdr.strip().split()
		H = [(item, count) for item, count in Counter(hdr).items() if count > 1]	
		if len(H) > 0:
			print('[!] WARNING: internal header collisions found')
			print('### FIELD, DUPLICATIONS:')
			for h in H:
				print('#  ', h[0] + ',', h[1])
		else:
			print('[!] No collisions found.')
	
	else:
		print('# Checking bindings number ...')
		
		if Op['-collision'] == None:
			inn = [sys.argv[2]]
		else:
			inn = [sys.argv[2], sys.argv[4]]
		
		for x in inn:
			c = 1
			han = open(x, 'r')
			if Op['-t']:
				han.readline()
			line = han.readline().strip().split()
			r = len(line)
			while line != []:
				line = han.readline().strip().split()
				c += 1
				t = len(line)
				if t != r and c < fileLen(x):
					print('[!] BindingError in file', os.path.basename(x))
					raise OSError('Incorrect number of bindings at line ' + str(c))
				else:
					r = t	
		
		if len(inn) == 1:
			print('[!] No errors found.')
		else:
			print('[!] Correct number of bindings.')
			print('# Checking field names collision ...')
			err = 0
			han1 = open(sys.argv[2], "r")
			han2 = open(sys.argv[4], "r")
			H1 = han1.readline().strip().split()
			H2 = han2.readline().strip().split()
			han1.close()
			han2.close()
			c = 0; I = []
			for x in H2:
				if x in H1:
					print('[!] field collision:', x)
					err += 1
					I += [c]
				c += 1
			if err > 0:
				print('[!] Warning:', err, 'field collisions found.')
				print('--------------------------------------------' +\
				      '---')
				ans = raw_input('Write new field names for ' +\
								sys.argv[4] +\
								'\nType tmp for automatic correction' +\
								'\nType ENTER to abort\n' +\
								'-----------------------------------' +\
								'------------\n')
				ans = ans.strip().split()
				if ans == ['tmp']:
					for i in range(err):
						H2[I[i]] = 'tmp_' + H2[I[i]]
				elif len(ans) == err:
					for i in range(err):
						H2[I[i]] = ans[i]
				else:
					raise ValueError('Aborted!')
				rmHead(sys.argv[4])
				addHead(sys.argv[4], '\t'.join(H2))
				print('[!] File', os.path.basename(sys.argv[4]) +\
				      ': field names updated.')
			else:
				'[!]', err, 'no collisions found.'
	
	print('# Done.')


elif sys.argv[1] in ("join", "collide"):
	Op = readOp(sys.argv, collideDefault)
	msg = {'collide': 'files', 'join': 'tables'}
	
	if Op['-time']:
		start_time = time.time()
		
	if sys.argv[1] == 'collide':
		
		if not Op['-v']:
			print('# Checking tables integrity ...',
)
		if Op['-a'] != None:
			Op['-a1'] = Op['-a']
			Op['-a2'] = 'tmp_' + Op['-a']
		tableCheck(Op['-t1'], Op['-t2'], collisionCheck = True,
		           verbose = not(Op['-v']))
		
		if not Op['-v']:
			print('# Preparing files for joining ...')
		
		if sys.argv[1] == 'collide':
			if Op['-s'] == None:
				han = open(Op['-t1'], 'r')
				hdr1 = ', '.join(han.readline().strip().split())
				han.close()
				han = open(Op['-t2'], 'r')
				hdr2 = ', '.join(han.readline().strip().split())
				han.close()
				Op['-s'] = hdr1 + ', ' + hdr2
			else:
				for x in Op['-s'].split(', '):
					if x == '_t1':
						han = open(Op['-t1'], 'r')
						hdr1 = ', '.join(han.readline().strip().split())
						han.close()
						Op['-s'] = re.sub('_t1', hdr1, Op['-s'])
					if x == '_t2':
						han = open(Op['-t2'], 'r')
						hdr2 = ', '.join(han.readline().strip().split())
						han.close()
						Op['-s'] = re.sub('_t2', hdr2, Op['-s'])
		#print(Op['-s'], '#', len(Op['-s'].split(', ')))
		t1 = Op['-t1']
		t2 = Op['-t2']
		Op['-t1'] = os.path.basename(Op['-t1']).split('.')[0]
		Op['-t2'] = os.path.basename(Op['-t2']).split('.')[0]
		Op['-d'] = t1.split('.')[0] + '.idb'
		
		try:
			tab2db(t1)
			tab2db(t2, db = Op['-d'])
		except Exception as inst:
			err = inst
			print(err)
			try:
				os.remove(Op['-d'])
				exit()
			except:
				pass
				exit()
	
	if not Op['-v']:
		print('# Joining ' + msg[sys.argv[1]] + ' ...')
	
	try:
		tJoin(Op['-d'], Op['-t1'], Op['-t2'], Op['-s'], Op['-j'],
		      Op['-a1'], Op['-a2'], Op['-c'], Op['-ord'], Op['-o'],
		      not(Op['-v']))
	except Exception as inst:
		err = inst
		print(err)
		try:
			os.remove(Op['-d'])
			exit()
		except:
			exit()
	
	if sys.argv[1] == 'collide' and Op['-rm']:
		os.remove(Op['-d'])
	
	if Op['-a'] != None or Op['-a1'] != None and Op['-a2'] != None:
		restoreBindings(t2, verbose = not(Op['-v']))
	else:
		restoreBindings(t2, verbose = False)
	
	if Op['-time']:
		print('# Time elapsed: ' + str(time.time() - start_time) +\
		      ' sec')
	
	if not Op['-v']:
		print('# Done.')


elif sys.argv[1] == "difference":
	Op = readOp(sys.argv, collideDefault)
	
	if not Op['-v']:
		print('# Please, wait ...')
	
	if Op['-time']:
		start_time = time.time()
	
	dbdiff(sys.argv[2], Op['-t1'], Op['-t2'], Op['-w'], Op['-a'],
	       Op['-o'], not(Op['-v']))
	
	if Op['-time']:
		print('# Time elapsed: ' + str(time.time() - start_time) +\
		      ' sec')
	
	if not Op['-v']:
		print('# Done.')


else:
	print('# Kew Toolkit v0.1.1b')
	print('[!] Value Error: ' + sys.argv[1] + ': invalid command')
	print("# Done.")

