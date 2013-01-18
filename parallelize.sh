#! /bin/bash
#  Name: Sravan Bhamidipati
#  Date: 18th January, 2013
#  Purpose: To find the precision and recall for many different combinations of alpha, beta and threshold.

analyze_file=$1
save_file=$2
parallel=$3
step=0.2

if [ $# -ne 3 ]; then
	echo "Usage: $0 <analyze_file> <save_file> <parallel>"
	exit 65
fi

for a in `seq 0 $step 0.8`
do
	a2=`echo $a $step | awk '{print $1+$2}'`
	for b in `seq 0 $step 0.8`
	do
		b2=`echo $b $step | awk '{print $1+$2}'`
		sed -i "s/^ALPHAS.*/ALPHAS = adLib.float_range($a, $a2, 0.01)/g; s/^BETAS.*/BETAS = adLib.float_range($b, $b2, 0.01)/g" adGlobals.py

		while [ `ps -ef | grep -c adwiser` -gt $parallel ]
		do
			sleep 5
		done

		./experiments.py $analyze_file > tests/tmp_a${a}_b${b}.txt &
		sleep 5
	done
done
wait

cat tests/tmp_a*.txt > $save_file
rm tests/tmp_a*.txt
