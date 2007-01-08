#!/bin/bash -x
procs="8 16 32 64"
#procs="64"
#reps=10
#reps=6
reps=1
#locktypes="-1 0 1 2"
locktypes="1 2"
lsname=$1
lsport=46822

for proc in $procs; do
    #rm -f results-$proc
    for locktype in $locktypes; do
        i=1
        while (( i <= $reps )); do
            #~/mpich-local/bin/mpiexec -machinefile $HOME/machines.in -np $proc ./flash-io listio -lsname $lsname -lsport $lsport -locktype $locktype 2>/dev/null | tee -a results-$proc
            ~/mpich-local/bin/mpiexec -np $proc ./flash-io listio -lsname $lsname -lsport $lsport -locktype $locktype
            (( i = $i + 1 ))
        done
    done
done
