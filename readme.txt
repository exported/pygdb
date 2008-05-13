pygdb
=====

This is a simple python wrapper around GDB. Currently the 
focus of this module is to provide the following:

    * Attach to existing processes
    * Create a new process from an executable
    * Callback/event or other mechanism for detecting 
      the debugger has caught an exception/breakpoint/AV
    * Ability to get a stack trace, dump registers and 
      create a dump file (core)
    * Works on last two versions of OS X
    * Works on Linux
    * Module works when run in a worker thread in Python 

Feature requests, bugs, etc can be sent to mike@phed.org.
