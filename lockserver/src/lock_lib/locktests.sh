#!/bin/bash -x

procs="8 27 64"
#reps=10
reps=1
mpirun=$HOME/mpich-local/bin/mpiexec
lsname=$1
lsport=46822
#locktypes="-1 0 1 2"
locktypes="1 2"
gsizes="100"

for proc in $procs; do
  for gsize in $gsizes; do
    for locktype in $locktypes; do
        case "$locktype" in
            -1 ) type="nolock";;
            0  ) type="filelock";;
            1  ) type="regionlock";;
            2  ) type="listlock";;
        esac

        #echo rm -f $type$gsize-$proc.results
        #rm -f $type$gsize-$proc.results
        i=1
        while (( i <= $reps )); do
           $mpirun -np $proc ./coll_perf -write -posix -gsize $gsize -filename /pvfs/scratch/aarestad/hi2 -lsname $lsname -lsport $lsport -locktype $locktype
           #$mpirun -machinefile ~/machines.in -np $proc ./coll_perf -write -posix -gsize $gsize -filename /pvfs/scratch/aarestad/hi2 -lsname $lsname -lsport $lsport -locktype $locktype >/dev/null 2>>$type$gsize-$proc.results
           (( i = i + 1 ))
        done
    done
  done
done
