#! /bin/bash
#  Name: Sravan Bhamidipati
#  Date: 13th November, 2012
#  Purpose: Find relevant and irrelevant ads related to all Ds.

if [ $# -ne 1 ]; then
	echo "Usage: $0 <all|one>"
	exit 65
fi

if [ $1 == "all" ]; then
	for ((d=11; d<=20; d++))
	do
		sed -i "s/^N\t/Y\t/g; s/^Y\(.*\)$d/N\1$d/g" all.cf 
		python adwiser.py all.cf 1 > all$d.txt
		mkdir results/all$d
		mv *.txt results/all$d
	done
elif [ $1 == "one" ]; then
	for ((d=11; d<=20; d++))
	do
		sed -i "s/^N\(.*\)[0-9][0-9]/N\1$d/g" one.cf 
		python adwiser.py one.cf 1 > one$d.txt
		mkdir results/one$d
		mv *.txt results/one$d
	done
fi
