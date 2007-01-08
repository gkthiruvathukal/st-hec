#!/bin/bash -x
proc=6
#reps=5
reps=1
frame_prefix="/pvfs/scratch/aarestad/frame"
frame_ext=".pnm"
machines="$HOME/machines.in"
output="output.txt"
mpirun=$HOME/mpich-local/bin/mpiexec
ex="lizard-listio-tile"
lsname=$1
lsport=46822
#locktypes="-1 0 1 2"
locktypes="1 2"

rm -f $output

fix_start ()
{
  case "$start" in
    0   ) start=50
          end=99 ;;
    50  ) start=100
          end=149 ;;
    100 ) start=150
          end=199 ;;
    150 ) start=200
          end=249 ;;
    200 ) start=250
          end=299 ;;
    250 ) start=300
          end=349 ;;
    300 ) start=350
          end=399 ;;
    350 ) start=400
          end=449 ;;
    400 ) start=450
          end=499 ;;
    450 ) start=0
          end=49 ;;
    *   ) echo "error in program"    
  esac
}

start=450
#end=499
end=474

for cur_ex in $ex; do
    for locktype in $locktypes; do
        for ((a=0; a < $reps; a++)); do
            #fix_start
            #$mpirun -machinefile $machines -np $proc $cur_ex $frame_prefix $frame_ext $start $end 6 $lsname $lsport $locktype | tee -a $output
            $mpirun -np $proc $cur_ex $frame_prefix $frame_ext $start $end 6 $lsname $lsport $locktype
        done
    done
done

if false; then
fix_start
for locktype in $locktypes; do
    echo mpirun -machinefile $machines -np $proc lizard-frame $frame_prefix $frame_ext $start $end 6 $lsname $lsport $locktype
    #mpirun -machinefile $machines -np $proc lizard-frame $frame_prefix $frame_ext $start $end 6 $lsname $lsport $locktype >> $output
done
fi

exit 0
