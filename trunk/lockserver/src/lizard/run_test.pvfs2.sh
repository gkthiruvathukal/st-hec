#!/bin/sh
proc=6
reps=3
frame_prefix="pvfs2:/mnt/pvfs2/frame"
frame_ext=".pnm"
machines="machines"
output="output.txt"
ex="lizard-tile lizard-coll-tile lizard-listio-tile lizard-dtype-tile"

rcp ching@chiba.mcs.anl.gov:pvfs-1.5.5/utils/u2p .
create_500_frames.sh

rm $output
rm $machines
echo cat "$PBS_NODEFILE" ">" $machines
cat $PBS_NODEFILE > $machines

fix_start ()
{
  case "$start" in
    0   ) start=100
          end=199 ;;
    100 ) start=200
          end=299 ;;
    200 ) start=300
          end=399 ;;
    300 ) start=400
          end=499 ;;
    400 ) start=0
          end=99 ;;
    *   ) echo "error in program"    
  esac
}

start=400
end=499

for cur_ex in $ex
  do
    for ((a=0; a < $reps; a++))
      do
        fix_start
        echo mpirun -machinefile $machines -np $proc $cur_ex $frame_prefix $frame_ext $start $end 6
        mpirun -machinefile $machines -np $proc $cur_ex $frame_prefix $frame_ext $start $end 6 >> $output
    done
done

fix_start
echo mpirun -machinefile $machines -np $proc lizard-frame $frame_prefix $frame_ext $start $end 6
mpirun -machinefile $machines -np $proc lizard-frame $frame_prefix $frame_ext $start $end 6 >> $output
exit 0


	
