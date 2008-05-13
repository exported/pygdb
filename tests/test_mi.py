
import sys
import os
from pygdb import Gdb, GdbError

if __name__ == "__main__":
	def main():
		class MyHandler:
			def __init__(self, verbose=0, show_output=0):
				self.verbose = verbose
				self.show_output = show_output

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

			def on_log(self, text):
				if self.verbose: sys.stdout.write(text)

			def on_target(self, text):
				if self.show_output: sys.stdout.write('> ' + text)

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
					if frame.file:
						print '\t%s, at %s:%s' % (
							frame.func,
							frame.file,
							frame.line
						)
					else:
						print '\t%s' % (frame.func)
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

		verbose = 0
		show_output = 0
		for x in sys.argv:
			if x.startswith('-v'):
				verbose = int(x[2:])
			if x.startswith('-o'):
				show_output = 1
		handler = MyHandler(verbose, show_output)
		gdb = Gdb(handler, verbose)
		try:
			gdb.file('qi')
			print 'run to completion'
			result = gdb.run().wait()

			print_stack(gdb)
			#gdb.core('core')
			print_registers(gdb)
			result = gdb.start().wait()
			bp = result.bkptno
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

			gdb.break_delete(bp)

		except Exception, ex:
			import traceback
			traceback.print_exc()
		gdb.quit()
	main()
