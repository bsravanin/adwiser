#! /bin/bash

if [ $# -ne 2 ]; then
	echo "Usage $0 <link_root> <count>"
	exit 65
fi

link_root=$1
count=$2


root="/data/CloudAuditing/adwiser"

if [ $count == "del" ]; then
	for ((i=10; i<31; i++))
	do
		rm -rf $link_root/ccloudauditor$i/*
	done
else
	for ((i=10; i<31; i++))
	do
		mkdir -p $root/$link_root/ccloudauditor$i
		cd $root/$link_root/ccloudauditor$i
		for dir in `ls $root/logs2/ccloudauditor$i | head -$count`
		do
			ln -s $root/logs2/ccloudauditor$i/$dir . 
		done
	done

	cd $root
fi
