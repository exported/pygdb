import pygdb

if __name__ == "__main__":
	gdb = pygdb.Gdb(verbose=1)
	try:
		print gdb.version().wait()
		print gdb.file('qi').wait()
		print gdb.start().wait()
		print gdb.run().wait()
	except Exception, ex:
		print ex.message
	gdb.exit()
	gdb.wait()
