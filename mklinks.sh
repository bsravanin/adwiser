#! /bin/bash

if [ $# -ne 1 ]; then
	echo "Usage $0 <count>"
	exit 65
fi

count=$1

root="/data/CloudAuditing/adwiser"

if [ $count == "del" ]; then
	for ((i=10; i<31; i++))
	do
		rm -rf logs3/ccloudauditor$i/*
	done
else
	for ((i=10; i<31; i++))
	do
		cd $root/logs3/ccloudauditor$i
		for dir in `ls $root/logs2/ccloudauditor$i | head -$count`
		do
			ln -s $root/logs2/ccloudauditor$i/$dir . 
		done
	done

	cd $root
fi
