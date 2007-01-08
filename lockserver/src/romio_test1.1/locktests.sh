#!/bin/bash

rm -f ./nolock30.results
i=1
while (( i <= 100 )); do
    echo "Running nolock30 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.nolock -write -posix -gsize 30 -filename pvfs://pvfs/scratch/aarestad/hi2 -lsname j70 -lsport 46822 2>/dev/null | tee -a ./nolock30.results
    (( i = i + 1 ))
done

rm -f ./nolock50.results
i=1
while (( i <= 100 )); do
    echo "Running nolock50 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.nolock -write -posix -gsize 50 -filename pvfs://pvfs/scratch/aarestad/hi2 -lsname j70 -lsport 46822 2>/dev/null | tee -a ./nolock50.results
    (( i = i + 1 ))
done

rm -f ./nolock100.results
i=1
while (( i <= 100 )); do
    echo "Running nolock100 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.nolock -write -posix -gsize 100 -filename pvfs://pvfs/scratch/aarestad/hi2 -lsname j70 -lsport 46822 2>/dev/null | tee -a ./nolock100.results
    (( i = i + 1 ))
done

rm -f ./filelock30.results
i=1
while (( i <= 100 )); do
    echo "Running filelock30 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.filelock -write -posix -gsize 30 -filename pvfs://pvfs/scratch/aarestad/hi2 -lsname j70 -lsport 46822 2>/dev/null | tee -a ./filelock30.results
    (( i = i + 1 ))
done

rm -f ./filelock50.results
i=1
while (( i <= 100 )); do
    echo "Running filelock50 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.filelock -write -posix -gsize 50 -filename pvfs://pvfs/scratch/aarestad/hi2 -lsname j70 -lsport 46822 2>/dev/null | tee -a ./filelock50.results
    (( i = i + 1 ))
done

rm -f ./filelock100.results
i=1
while (( i <= 100 )); do
    echo "Running filelock100 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.filelock -write -posix -gsize 100 -filename pvfs://pvfs/scratch/aarestad/hi2 -lsname j70 -lsport 46822 2>/dev/null | tee -a ./filelock100.results
    (( i = i + 1 ))
done

rm -f ./regionlock30.results
i=1
while (( i <= 100 )); do
    echo "Running regionlock30 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.regionlock -write -posix -gsize 30 -filename pvfs://pvfs/scratch/aarestad/hi2 -lsname j70 -lsport 46822 2>/dev/null | tee -a ./regionlock30.results
    (( i = i + 1 ))
done

rm -f ./regionlock50.results
i=1
while (( i <= 100 )); do
    echo "Running regionlock50 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.regionlock -write -posix -gsize 50 -filename pvfs://pvfs/scratch/aarestad/hi2 -lsname j70 -lsport 46822 2>/dev/null | tee -a ./regionlock50.results
    (( i = i + 1 ))
done

rm -f ./regionlock100.results
i=1
while (( i <= 100 )); do
    echo "Running regionlock100 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.regionlock -write -posix -gsize 100 -filename pvfs://pvfs/scratch/aarestad/hi2 -lsname j70 -lsport 46822 2>/dev/null | tee -a ./regionlock100.results
    (( i = i + 1 ))
done

rm -f ./listlock30.results
i=1
while (( i <= 100 )); do
    echo "Running listlock30 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.listlock -write -posix -gsize 30 -filename pvfs://pvfs/scratch/aarestad/hi2 -lsname j70 -lsport 46822 2>/dev/null | tee -a ./listlock30.results
    (( i = i + 1 ))
done

rm -f ./listlock50.results
i=1
while (( i <= 100 )); do
    echo "Running listlock50 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.listlock -write -posix -gsize 50 -filename pvfs://pvfs/scratch/aarestad/hi2 -lsname j70 -lsport 46822 2>/dev/null | tee -a ./listlock50.results
    (( i = i + 1 ))
done

rm -f ./listlock100.results
i=1
while (( i <= 100 )); do
    echo "Running listlock100 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.listlock -write -posix -gsize 100 -filename pvfs://pvfs/scratch/aarestad/hi2 -lsname j70 -lsport 46822 2>/dev/null | tee -a ./listlock100.results
    (( i = i + 1 ))
done
