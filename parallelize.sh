#! /bin/bash
#  Name: Sravan Bhamidipati
#  Date: 19th January, 2013
#  Purpose: To find the precision and recall for many different combinations of alpha, beta and threshold.

analyze_file=$1
save_file=$2
parallel=$3
a_step=0.25
a_last=0.75
b_step=0.5
b_last=0.5

if [ $# -ne 3 ]; then
	echo "Usage: $0 <analyze_file> <save_file> <parallel>"
	exit 65
fi

for a in `seq 0 $a_step $a_last`
do
	a2=`echo $a $a_step | awk '{print $1+$2}'`
	for b in `seq 0 $b_step $b_last`
	do
		b2=`echo $b $b_step | awk '{print $1+$2}'`
		sed -i "s/^ALPHAS.*/ALPHAS = adLib.float_range($a, $a2, 0.01)/g; s/^BETAS.*/BETAS = adLib.float_range($b, $b2, 0.01)/g" adGlobals.py

		while [ `ps -ef | awk 'BEGIN {sum=0} {if($0~/experiments.py/ && $0!~/awk/) sum++} END {print sum}'` -ge $parallel ]
		do
			sleep 1
		done

		./experiments.py $analyze_file > tests/tmp_a${a}_b${b}.txt &
		sleep 3
	done
done
wait

cat tests/tmp_a*.txt > $save_file
rm tests/tmp_a*.txt
