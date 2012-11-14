#! /bin/bash
#  Name: Sravan Bhamidipati
#  Date: 13th November, 2012
#  Purpose: Find relevant and irrelevant ads related to all Ds.

for ((d=11; d<=20; d++))
do
	sed -i "s/^N\t/Y\t/g; s/^Y\(.*\)$d/N\1$d/g" debug.cf
	python adwiser.py debug.cf 1 > debug$d.txt
	mkdir results/debug$d
	mv *.txt results/debug$d
done
