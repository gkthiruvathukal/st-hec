#!/bin/bash

rm -f ./noionolock30.results
i=1
while (( i <= 100 )); do
    echo "Running noionolock30 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.noionolock -write -posix -gsize 30 -filename hi2 -lsname $1 -lsport 46822 | tee -a ./noionolock30.results
    (( i = i + 1 ))
done

rm -f ./noionolock50.results
i=1
while (( i <= 100 )); do
    echo "Running noionolock50 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.noionolock -write -posix -gsize 50 -filename hi2 -lsname $1 -lsport 46822 2>/dev/null | tee -a ./noionolock50.results
    (( i = i + 1 ))
done

rm -f ./noionolock100.results
i=1
while (( i <= 100 )); do
    echo "Running noionolock100 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.noionolock -write -posix -gsize 100 -filename hi2 -lsname $1 -lsport 46822 2>/dev/null | tee -a ./noionolock100.results
    (( i = i + 1 ))
done

rm -f ./noiofilelock30.results
i=1
while (( i <= 100 )); do
    echo "Running noiofilelock30 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.noiofilelock -write -posix -gsize 30 -filename hi2 -lsname $1 -lsport 46822 2>/dev/null | tee -a ./noiofilelock30.results
    (( i = i + 1 ))
done

rm -f ./noiofilelock50.results
i=1
while (( i <= 100 )); do
    echo "Running noiofilelock50 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.noiofilelock -write -posix -gsize 50 -filename hi2 -lsname $1 -lsport 46822 2>/dev/null | tee -a ./noiofilelock50.results
    (( i = i + 1 ))
done

rm -f ./noiofilelock100.results
i=1
while (( i <= 100 )); do
    echo "Running noiofilelock100 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.noiofilelock -write -posix -gsize 100 -filename hi2 -lsname $1 -lsport 46822 2>/dev/null | tee -a ./noiofilelock100.results
    (( i = i + 1 ))
done

rm -f ./noioregionlock30.results
i=1
while (( i <= 100 )); do
    echo "Running noioregionlock30 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.noioregionlock -write -posix -gsize 30 -filename hi2 -lsname $1 -lsport 46822 2>/dev/null | tee -a ./noioregionlock30.results
    (( i = i + 1 ))
done

rm -f ./noioregionlock50.results
i=1
while (( i <= 100 )); do
    echo "Running noioregionlock50 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.noioregionlock -write -posix -gsize 50 -filename hi2 -lsname $1 -lsport 46822 2>/dev/null | tee -a ./noioregionlock50.results
    (( i = i + 1 ))
done

rm -f ./noioregionlock100.results
i=1
while (( i <= 100 )); do
    echo "Running noioregionlock100 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.noioregionlock -write -posix -gsize 100 -filename hi2 -lsname $1 -lsport 46822 2>/dev/null | tee -a ./noioregionlock100.results
    (( i = i + 1 ))
done

rm -f ./noiolistlock30.results
i=1
while (( i <= 100 )); do
    echo "Running noiolistlock30 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.noiolistlock -write -posix -gsize 30 -filename hi2 -lsname $1 -lsport 46822 2>/dev/null | tee -a ./noiolistlock30.results
    (( i = i + 1 ))
done

rm -f ./noiolistlock50.results
i=1
while (( i <= 100 )); do
    echo "Running noiolistlock50 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.noiolistlock -write -posix -gsize 50 -filename hi2 -lsname $1 -lsport 46822 2>/dev/null | tee -a ./noiolistlock50.results
    (( i = i + 1 ))
done

rm -f ./noiolistlock100.results
i=1
while (( i <= 100 )); do
    echo "Running noiolistlock100 test $i of 100"
    mpirun -np 8 -machinefile ~/machines.in ./coll_perf.noiolistlock -write -posix -gsize 100 -filename hi2 -lsname $1 -lsport 46822 2>/dev/null | tee -a ./noiolistlock100.results
    (( i = i + 1 ))
done
