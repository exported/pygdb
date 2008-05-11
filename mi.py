#!/usr/bin/python

import os
import mi_parser
import threading
from subprocess import *

GDB_PROMPT = '(gdb) \n'
GDB_CMDLINE = 'gdb -n -q -i mi'

def flatten(x):
	"""flatten(sequence) -> list

	Returns a single, flat list which contains all elements retrieved
	from the sequence and all recursively contained sub-sequences
	(iterables).

	Examples:
	>>> [1, 2, [3,4], (5,6)]
	[1, 2, [3, 4], (5, 6)]
	>>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
	[1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""

	result = []
	for el in x:
		#if isinstance(el, (list, tuple)):
		if hasattr(el, "__iter__") and not isinstance(el, basestring):
			result.extend(flatten(el))
		else:
			result.append(el)
	return result

class GdbConsole:
	def __init__(self):
		self.proc = Popen(GDB_CMDLINE, 0, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)

	def read_until_prompt(self):
		lines = []
		while(True):
			line = self.proc.stdout.readline()
			#print line
			if not line or line == GDB_PROMPT:
				return lines
			lines.append(line)

	def send_cmd(self, cmd):
		cmd_line = cmd + '\n'
		self.proc.stdin.write(cmd_line)
		#sys.stdout.write('$ ' + cmd_line)

class GdbReader:
	def __init__(self, gdb, dispatcher):
		self.__gdb = gdb
		self.__console = gdb.console
		self.__dispatcher = dispatcher
		self.__thread = threading.Thread(target=self.__run_loop, name='GdbReader')
		self.__thread.setDaemon(True)

	def start(self):
		self.__thread.start()

	def stop(self):
		self.__thread.join()

	def __run_loop(self):
		while(True):
			lines = self.__console.read_until_prompt()
			if not lines:
				break

			for line in lines:
				try:
					output = mi_parser.process(line)
					self.__process_output(output)
				except Exception, ex:
					print 'parsing error: %s' % ex.message
					print 'for gdb output: %s' % output

	def __process_output(self, output):
		for record in output.records:
			callback = getattr(self.__dispatcher, 'on_' + record.type)
			callback(record)

class InferiorReader:
	def __init__(self, gdb, dispatcher):
		self.__gdb = gdb
		self.__dispatcher = dispatcher
		self.__thread = threading.Thread(target=self.__run_loop, name='InferiorReader')
		self.__thread.setDaemon(True)

	def start(self):
		self.__master, self.__slave = os.openpty()
		self.__stdout = os.fdopen(self.__master)
		self.__tty = os.ttyname(self.__slave)
		self.__gdb.inferior_tty_set(self.__tty)
		self.__thread.start()

	def stop(self):
		#print 'close slave'
		os.close(self.__slave)
		#print 'close master'
		self.__stdout.close()
		#print 'join'
		self.__thread.join()

	def __run_loop(self):
		while(True):
			line = self.__stdout.readline()
			if not line:
				break
			print 'inferior: %s' % line

class Gdb:
	def __init__(self, handler=None, verbose=0):
		self.console = GdbConsole()
		self.console.read_until_prompt()
		self.verbose = verbose
		self.__next_token = 1
		self.__dispatcher = GdbDispatcher(self, handler)
		self.__reader = GdbReader(self, self.__dispatcher)
#		self.__inferior = InferiorReader(self, self.__dispatcher)
		self.__reader.start()
#		self.__inferior.start()

	def _cmd(self, cmd, args=None):
		if args is not None:
			if isinstance(args, list):
				opts = ''
				flat = flatten(args)
				for arg in flat:
					if arg is not None:
						opts += str(arg) + ' '
				args = opts
			else:
				args = str(args)
			cmd = cmd + ' ' + args

		token = str(self.__next_token)
		cmd = token + cmd
		self.__next_token += 1

		ar = GdbAsyncResult(self.__dispatcher, token)
		self.console.send_cmd(cmd)
		return ar

####################################################
	# general
	def wait(self):
		self.__reader.stop()
#		self.__inferior.stop()

	def help(self):
		return self._cmd('h')

	def list_features(self):
		return self._cmd('-list-features')

	def enable_timings(self, flag):
		return self._cmd('-enable-timings', flag)

	def interpreter_exec(self, interpreter, command):
		'''use this with caution, the output is not parsable'''
		return self._cmd('-interpreter-exec', [ interpreter, command ])

	def inferior_tty_set(self, tty):
		return self._cmd('-inferior-tty-set', tty)

	def inferior_tty_show(self):
		return self._cmd('-inferior-tty-show')

	def start(self, entry='main', args=None):
		self.break_insert(entry)
		return self.run(args)

	def quit(self):
		self.kill()
		self.exit()
		self.wait()

####################################################
	# gdb
	def exit(self):
		return self._cmd('-gdb-exit')

	def version(self):
		return self._cmd('-gdb-version')

	def set(self):
		return self._cmd('-gdb-set')

	def show(self):
		return self._cmd('-gdb-show')

####################################################
	# file
	def file(self, filename):
		return self._cmd('-file-exec-and-symbols', filename)

	def file_exec_file(self, filename):
		return self._cmd('-file-exec-flie', filename)

	def file_list_sections(self):
		return self._cmd('-file-list-exec-sections')

	def file_source(self):
		return self._cmd('-file-list-exec-source-file')

	def file_list_sources(self):
		return self._cmd('-file-list-exec-source-files')

	def file_list_shared_libs(self):
		return self._cmd('-file-list-shared-libraries')

	def file_list_symbol_files(self):
		return self._cmd('-file-list-symbol-files')

	def file_symbol_file(self, filename):
		return self._cmd('-file-symbol-file', filename)

####################################################
	# target
	def core(self, filename):
		return self._cmd('target core', filename)

	def attach(self, args):
		return self._cmd('-target-attach', args)

	def detach(self):
		return self._cmd('-target-detach')

	def target_compare_sections(self, section=None):
		return self._cmd('-target-compare-sections', section)

	def disconnect(self):
		return self._cmd('-target-disconnect', section)

	def download(self):
		return self._cmd('-target-download')

	def target_exec_status(self):
		return self._cmd('-target-exec-status')

	def target_list_available_targets(self):
		return self._cmd('-target-list-available-targets')

	def target_list_current_targets(self):
		return self._cmd('-target-list-current-targets')

	def target_list_parameters(self):
		return self._cmd('-target-list-parameters')

	def target_select(self, type, parameters):
		return self._cmd('-target-list-parameters', [ type, parameters ])

####################################################
	# stack
	def stack_info_frame(self):
		return self._cmd('-stack-info-frame')

	def stack_info_depth(self, max_depth=None):
		return self._cmd('-stack-info-depth', max_depth)

	def stack_list_arguments(self, show_values=1, low_frame=None, high_frame=None):
		args = [ show_values, low_frame, high_frame ]
		return self._cmd('-stack-list-arguments', args)

	def stack_list_frames(self, low_frame=None, high_frame=None):
		return self._cmd('-stack-list-frames', [ low_frame, high_frame ])

	def stack_list_locals(self, print_values=1):
		return self._cmd('-stack-list-locals', print_values)

	def stack_select_frame(self, num):
		return self._cmd('-stack-select-frame', num)

####################################################
	# data
	def data_disassemble(self, mode, start_addr=None, end_addr=None, filename=None, linenum=None, lines=None):
		'''-data-disassemble [ -s start-addr -e end-addr ] | [ -f filename -l linenum [ -n lines ] ] -- mode'''
		args = []
		if start_addr: args.extend(['-s', start_addr])
		if end_addr: args.extend(['-e', end_addr])
		if filename: args.extend(['-f', filename])
		if linenum: args.extend(['-l', linenum])
		if lines: args.extend(['-n', lines])
		args.append('---')
		args.append(mode)
		return self._cmd('-data-disassemble', args)

	def data_evaluate_expression(self, expr):
		'''-data-evaluate-expression expr'''
		return self._cmd('-data-evaluate-expression', expr)

	def data_list_changed_registers(self):
		'''-data-list-changed-registers'''
		return self._cmd('-data-list-changed-registers')

	def data_list_register_names(self, regno=None):
		'''-data-list-register-names [ ( regno )+ ]'''
		return self._cmd('-data-list-register-names', regno)

	def data_list_register_values(self, fmt='r', regno=None):
		'''-data-list-register-values fmt [ ( regno )*]'''
		return self._cmd('-data-list-register-values', [ fmt, regno ])

	def data_read_memory(self, address, word_format, word_size, nr_rows, nr_cols, byte_offset=None, aschar=None):
		'''-data-read-memory [ -o byte-offset ] address word-format word-size nr-rows nr-cols [ aschar ]'''
		args = []
		if byte_offset: args.extend(['-o', byte_offset])
		args.extend([ address, word_format, word_size, nr_rows, nr_cols, aschar ])
		return self._cmd('-data-read-memory', args)

####################################################
	# exec
	def kill(self):
		return self._cmd('-exec-abort')

	def set_args(self, args):
		return self._cmd('-exec-arguments', args)

	def show_args(self, args):
		return self._cmd('-exec-show-arguments')

	def continue_(self):
		return self._cmd('-exec-continue')

	def run(self, args=None):
		if args: self.set_args(args)
		return self._cmd('-exec-run')

	def step(self):
		return self._cmd('-exec-step')

	def stepi(self):
		return self._cmd('-exec-step-instruction')

	def next(self):
		return self._cmd('-exec-next')

	def nexti(self):
		return self._cmd('-exec-next-instruction')

	def finish(self):
		return self._cmd('-exec-finish')

	def interrupt(self):
		return self._cmd('-exec-interrupt')

	def return_(self):
		return self._cmd('-exec-return')

	def until(self, location=None):
		return self._cmd('-exec-until', location)

####################################################
	# environment
	def env_cd(self, pathdir):
		'''-environment-cd pathdir'''
		return self._cmd('-environment-cd', pathdir)

	def env_dir(self, pathdir=None, reset=False):
		'''-environment-directory [ -r ] [ pathdir ]+'''
		args = []
		if reset: args.append('-r')
		args.append(pathdir)
		return self._cmd('-environment-directory', args)

	def env_path(self, pathdir=None, reset=False):
		'''-environment-path [ -r ] [ pathdir ]+'''
		args = []
		if reset: args.append('-r')
		args.append(pathdir)
		return self._cmd('-environment-path', args)

	def env_pwd(self):
		'''-environment-pwd'''
		return self._cmd('-environment-pwd')

####################################################
	# breakpoints
	def break_after(self, number, count):
		'''-break-after number count'''
		return self._cmd('-break-after', number, count)

	def break_condition(self, number, expr):
		'''-break-condition number expr'''
		return self._cmd('-break-condition', number, expr)

	def break_delete(self, bp):
		'''-break-delete ( bp )+'''
		return self._cmd('-break-delete', bp)

	def break_disable(self, bp):
		'''-break-disable ( bp )+'''
		return self._cmd('-break-disable', bp)

	def break_enable(self, bp):
		'''-break-enable ( bp )+'''
		return self._cmd('-break-enable', bp)

	def break_info(self, bp):
		'''-break-info ( bp )+'''
		return self._cmd('-break-info', bp)

	def break_insert(self, location, temp=False, hardware=False, regular=False, condition=None, ignore_count=None, thread=None):
		'''-break-insert [ -t ] [ -h ] [ -r ] [ -c condition ] [ -i ignore-count ] [ -p thread ] location'''
		args = []
		if temp: args.append('-t')
		if hardware: args.append('-h')
		if regular: args.append('-r')
		if condition: args.extend(['-c', condition])
		if ignore_count: args.extend(['-i', ignore_count])
		if thread: args.extend(['-p', thread])
		args.append(location)
		return self._cmd('-break-insert', args)

	def break_list(self):
		'''-break-list'''
		return self._cmd('-break-list')

	def break_watch(self, expr, access=False, read=False):
		'''-break-watch [ -a | -r ] expr'''
		args = []
		if access: args.append('-a')
		if read: args.append('-r')
		args.append(expr)
		return self._cmd('-break-watch', args)

####################################################
	# thread
	def thread_info(self, num=None):
		return self._cmd('-thread-info', num)

	def thread_list_ids(self):
		return self._cmd('-thread-list-ids')

	def thread_select(self, num):
		return self._cmd('-thread-select', num)

class GdbError(Exception): pass

class GdbAsyncResult:
	def __init__(self, dispatcher, token):
		self.__dispatcher = dispatcher
		self.__condition = threading.Condition()
		self.token = token
		self.result = None
		self.status = 'pending'
		self.__dispatcher.register_token(self.token, self.__on_complete)

	def __on_complete(self, status, result):
		try:
			self.__condition.acquire()
			self.status = status
			self.result = result
			self.__condition.notify()
		finally:
			self.__condition.release()

	def wait(self):
		try:
			self.__condition.acquire()
			while not self.result:
				self.__condition.wait()
		finally:
			self.__condition.release()

		if self.status == 'error':
			raise GdbError, self.result.msg
		return self.result

class GdbDispatcher:
	def __init__(self, gdb, handler):
		self.__gdb = gdb
		self.__handler = handler
		if self.__handler: self.__handler.on_gdb(gdb)
		self.__delegates = {}

	def __print_event(self, event):
		if event.token:
			token = '[' + event.token + ']'
		else:
			token = ''
		print '%s: %s %s' % (event.type, token, event.class_)

	def __print_output(self, output):
		print '%s: %s' % (output.type, output.value)

	def __call_handler(self, method, args):
		if self.__handler and hasattr(self.__handler, method):
			attr = getattr(self.__handler, method)
			apply(attr, args)

	def __call_delegate(self, token, status, results):
		if self.__delegates.has_key(token):
			delegate = self.__delegates[token]
			delegate(status, results)
			self.__delegates.pop(token)

	def register_token(self, token, delegate):
		self.__delegates[token] = delegate

	def on_exec(self, event):
		if self.__gdb.verbose:
			self.__print_event(event)

		if self.__gdb.verbose >= 2:
			print event.result

		self.__call_delegate(event.token, event.class_, event.result)

		if event.class_ == 'stopped':
			self.__call_handler('on_stopped', [event])

	def on_result(self, event):
		if self.__gdb.verbose:
			self.__print_event(event)

		if self.__gdb.verbose >= 2:
			print event.result

		if event.class_ == 'running':
			self.__call_handler('on_running', [event])
		else:
			self.on_complete(event.token, event.class_, event.result)

	def on_notify(self, event):
		if self.__gdb.verbose:
			self.__print_event(event)
		self.__call_handler('on_notify', [event])

	def on_console(self, event):
		if self.__gdb.verbose:
			self.__print_output(event)
		self.__call_handler('on_console', [event])

	def on_target(self, event):
		if self.__gdb.verbose:
			self.__print_output(event)
		self.__call_handler('on_target', [event])

	def on_log(self, event):
		if self.__gdb.verbose:
			self.__print_output(event)
		self.__call_handler('on_log', [event])

	def on_complete(self, token, status, results):
		self.__call_delegate(token, status, results)
		if status == 'done':
			self.__call_handler('on_done', [token, results])
		elif status == 'error':
			self.__call_handler('on_error', [token, results])
		else:
			self.__call_handler('on_complete', [token, status, results])

if __name__ == "__main__":
	def main():
		class MyHandler:
			def __init__(self, verbose=0):
				self.verbose = verbose

			def on_gdb(self, gdb):
				self.__gdb = gdb

			def on_running(self, event):
				if self.verbose: print 'running'

			def on_stopped(self, event):
				if self.verbose: print 'stopped'

			def on_complete(self, token, status, results):
				if self.verbose: print 'complete'

			def on_error(self, token, results):
				print 'error: %s' % results

			def on_done(self, token, results):
				if self.verbose: print 'done'

		def print_locals(gdb):
			try:
				result = gdb.stack_list_locals().wait()
				print 'locals'
				for local in result.locals:
					print '\t%s = %s' % ( local.name, local.value )
			except GdbError, ex:
				print 'gdb error: ' + ex.message

		def print_arguments(gdb):
			try:
				result = gdb.stack_list_arguments().wait()
				print 'args'
				for frame in result.stack_args.frame:
					print '\tframe: ' + frame.level
					for arg in frame.args:
						print '\t\t%s = %s' % ( arg.name, arg.value )
			except GdbError, ex:
				print 'gdb error: ' + ex.message

		def print_stack(gdb):
			try:
				result = gdb.stack_list_frames().wait()
				print 'stack'
				for frame in result.stack.frame:
					print '\t%s, at %s:%s' %(
						frame.func,
						frame.file,
						frame.line
					)
			except GdbError, ex:
				print 'gdb error: ' + ex.message

		def print_registers(gdb, registers=None, header='registers'):
			try:
				names = gdb.data_list_register_names().wait()
				result = gdb.data_list_register_values(regno=registers).wait()
				print header
				for register in result.register_values:
					name = names.register_names[int(register.number)]
					print '\t%s: %s' % (name, register.value)
			except GdbError, ex:
				print 'gdb error: ' + ex.message

		def print_changed_registers(gdb):
			try:
				changed = gdb.data_list_changed_registers().wait()
				print_registers(gdb, changed.changed_registers, 'changed')
			except GdbError, ex:
				print 'gdb error: ' + ex.message

		handler = MyHandler()
		gdb = Gdb(handler)
		try:
			gdb.file('qi')
			#gdb.core('core')
			print_registers(gdb)
			result = gdb.start().wait()
			print 'start: bkptno: %s, reason: %s, thread-id: %s' % (
				result.bkptno,
				result.reason,
				result.thread_id
			)

			print_changed_registers(gdb)
			print_stack(gdb)
			print_arguments(gdb)
			print_locals(gdb)

			print 'step'
			result = gdb.step().wait()
			print_changed_registers(gdb)
			print 'step'
			result = gdb.step().wait()
			print_changed_registers(gdb)
			print 'step'
			result = gdb.step().wait()
			print_changed_registers(gdb)

			print_stack(gdb)
			print_arguments(gdb)
			print_locals(gdb)

			print 'run'
			gdb.run().wait()

			print 'sleep 1 second'
			import time
			time.sleep(1)

			print 'interrupt'
			result = gdb.interrupt().wait()
			print_stack(gdb)

			print 'run to completion'
			result = gdb.run().wait()

		except Exception, ex:
			print ex.message
		gdb.quit()
	main()
