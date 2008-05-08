#!/usr/bin/python

import sys
from subprocess import *

GDB_PROMPT = '(gdb) '
GDB_CMDLINE = 'gdb -n -q'

class GdbConsole:

	def __init__(self):
		self.output = ''
		self.proc = Popen(GDB_CMDLINE, 0, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)

	def read_until_prompt(self):
		buf = ''
		while(True):
			buf += self.proc.stdout.read(1)
			if len(buf) < len(GDB_PROMPT):
				continue

			if buf.endswith(GDB_PROMPT):
				outlen = len(buf) - len(GDB_PROMPT)
				self.output = buf[:outlen]
				return

	def send_cmd(self, cmd):
		cmd_line = cmd + '\n'
		self.proc.stdin.write(cmd_line)
#		sys.stdout.write('$ ' + cmd_line)

	def show_output(self):
		sys.stdout.write(self.output)

	def communicate(self, cmd):
		self.send_cmd(cmd)
		self.read_until_prompt()
#		self.show_output()
		return self.output
