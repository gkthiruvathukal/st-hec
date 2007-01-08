#!/bin/sh
pvfs_u2p="/home/aching/datatype/pvfs2/src/apps/admin/pvfs2-cp"
pvfs_dir="/mnt/pvfs2/"

#create the frames
read_file="frame0000.pnm"
var0=0
echo How many frames do you want in total?
read limit
while [ "$var0" -lt "$limit" ]
do
    case "$var0" in
    [0-9]           ) echo $pvfs_u2p $read_file $pvfs_dir"frame000"$var0.pnm 
		      $pvfs_u2p $read_file $pvfs_dir"frame000"$var0.pnm;;
    [1-9][0-9]      ) echo $pvfs_u2p $read_file $pvfs_dir"frame00"$var0.pnm
                      $pvfs_u2p $read_file $pvfs_dir"frame00"$var0.pnm;;
    [1-9][0-9][0-9] ) echo $pvfs_u2p $read_file $pvfs_dir"frame0"$var0.pnm
		      $pvfs_u2p $read_file $pvfs_dir"frame0"$var0.pnm;;
    *               ) echo $(($limit+1)) frames is too big;;
    esac
    var0=$(($var0+1))
done

exit 0
