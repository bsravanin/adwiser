#! /bin/bash
#  Name: Sravan Bhamidipati
#  Date: 22nd October, 2012
#  Purpose: Plot a bunch of graphs.

if [ $# -lt 3 ]; then
	echo "Usage: $0 <base_set> <test_set> <save_dir> [debug]"
	exit 65
fi

base=$1
test_root=$2
save_dir=$3

mkdir -p $save_dir

if [ -z $4 ]; then
	./comparer.py $base/inbox.html $test_root/inbox $save_dir/inbox.png
	for ((i=1; i<=10; i++))
	do
		./comparer.py $base/email$i.html $test_root/email$i $save_dir/email$i.png
	done
else
	./comparer.py $base/inbox.html $test_root/inbox $save_dir/inbox.png 1
	for ((i=1; i<=10; i++))
	do
		./comparer.py $base/email$i.html $test_root/email$i $save_dir/email$i.png
	done
fi
