# DONE
-break-after number count
-break-condition number expr
-break-delete ( bp )+
-break-disable ( bp )+
-break-enable ( bp )+
-break-info ( bp )+
-break-insert [ -t ] [ -h ] [ -f ] [ -c condition ] [ -i ignore-count ] [ -p thread ] location
-break-list
-break-watch [ -a | -r ] expr

# DONE
-exec-arguments args
-exec-show-arguments
-environment-cd pathdir
-environment-directory [ -r ] [ pathdir ]+
-environment-path [ -r ] [ pathdir ]+
-environment-pwd

# DONE
-thread-info [ thread-id ]
-thread-list-ids
-thread-select threadnum

# DONE
-exec-abort
-exec-continue
-exec-finish
-exec-interrupt
-exec-next
-exec-next-instruction
-exec-return
-exec-run
-exec-step
-exec-step-instruction
-exec-until [ location ]

# DONE
-stack-info-frame
-stack-info-depth [ max-depth ]
-stack-list-arguments show-values [ low-frame high-frame ]
-stack-list-frames [ low-frame high-frame ]
-stack-list-locals print-values
-stack-select-frame framenum

# TODO: if ever
-var-create
-var-delete
-var-set-format
-var-show-format
-var-info-num-children
-var-list-children
-var-info-type
-var-info-expression
-var-info-path-expression
-var-show-attributes
-var-evaluate-expression
-var-assign
-var-update
-var-set-frozen

# DONE
-data-disassemble [ -s start-addr -e end-addr ] | [ -f filename -l linenum [ -n lines ] ] -- mode
-data-evaluate-expression expr
-data-list-changed-registers
-data-list-register-names [ ( regno )+ ]
-data-list-register-values fmt [ ( regno )*]
-data-read-memory [ -o byte-offset ] address word-format word-size nr-rows nr-cols [ aschar ]

# TODO
-symbol-info-address symbol
-symbol-info-file
-symbol-info-function
-symbol-info-line
-symbol-info-symbol addr
-symbol-list-functions
-symbol-list-lines filename
-symbol-list-types
-symbol-list-variables
-symbol-locate
-symbol-type variable

# DONE
-file-exec-and-symbols file
-file-exec-file file
-file-list-exec-sections
-file-list-exec-source-file
-file-list-exec-source-files
-file-list-shared-libraries
-file-list-symbol-files
-file-symbol-file file

# DONE
-target-attach pid | file
-target-compare-sections [ section ]
-target-detach
-target-disconnect
-target-download
-target-exec-status
-target-list-available-targets
-target-list-current-targets
-target-list-parameters
-target-select type parameters ...

# TODO: if ever
-target-file-put hostfile targetfile
-target-file-get targetfile hostfile
-target-file-delete targetfile

# DONE
-gdb-exit
-gdb-set
-gdb-show
-gdb-version
-list-features
-interpreter-exec interpreter command
-inferior-tty-set /dev/pts/1
-inferior-tty-show
-enable-timings [yes | no]

