#!/bin/sh
proc=6
reps=3
frame_prefix="pvfs:/pvfs-auto/frame"
frame_ext=".pnm"
machines="machines"
output="output.txt"
ex="lizard-tile lizard-coll-tile lizard-listio-tile lizard-dtype-type"

rcp ching@chiba.mcs.anl.gov:pvfs-1.5.6-pre1/utils/u2p .
create_100_frames.sh

rm $output
rm $machines
echo cat "$PBS_NODEFILE" ">" $machines
cat "$PBS_NODEFILE" > $machines

start=0
end=99

for cur_ex in $ex
  do
    for ((a=0; a < $reps; a++))
      do
        echo mpirun -machinefile $machines -np $proc $cur_ex $frame_prefix $frame_ext $start $end 6
        mpirun -machinefile $machines -np $proc $cur_ex $frame_prefix $frame_ext $start $end 6 >> $output
    done
done

echo mpirun -machinefile $machines -np $proc lizard-frame $frame_prefix $frame_ext $start $end 6
mpirun -machinefile $machines -np $proc lizard-frame $frame_prefix $frame_ext $start $end 6 >> $output
exit 0


	
