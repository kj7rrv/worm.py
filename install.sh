#!/bin/bash

if [ "$1" == '' ]; then
	target="/usr/local/"
elif [ -d "$1" ]; then
	target=$1
else
	echo "Error: if an argument is present, it must be a directory" >&2
	exit 1
fi

if [ "$2" == '' ]; then
	final_target=$target
else
	final_target=$2
fi

mkdir -p $target/bin $target/share/wormpy

cp wormpy/*.py $target/share/wormpy
echo "#!/bin/bash" > $target/bin/wormpy
echo "python3 $final_target/share/wormpy/" >> $target/bin/wormpy
chmod +x $target/bin/wormpy
