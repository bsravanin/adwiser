#! /bin/bash
#  Name: Sravan Bhamidipati
#  Date: 7th November, 2012
#  Purpose: A wrapper around automate.py for multiple trials.

if [ $# -ne 4 ]; then
	echo "Usage: $0 <username> <password> <save_dir> <trials>"
	exit 65
fi

for ((i=1; i<=$4; i++))
do
	timestamp=`date +%F_%H-%M-%S`
	python automate.py $1 $2 $3/$timestamp
done
