SRC_DIRS="edu/northwestern/ece/lockserver info/jhpc"
PKG="edu.northwestern.ece.lockserver"
APPS="FileLockServerService FileLockClientService FileLockTestMain"

for app in $APPS
do
	gcj --main=$PKG.$app -o $app `find $SRC_DIRS -name '*.java'`
done
