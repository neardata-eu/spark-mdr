VIAHOME=$HOME/via

for n in $(echo "1 2 3"); do
	echo "-----------------------------"
	echo "Running iteration $n of MDR..."
	echo "-----------------------------"
	mkdir $VIAHOME/main/logs/it$n $VIAHOME/main/logs/spark-events/it$n
	for W in $(echo "1 2 3"); do
		echo "Number of WORKERS set to $W"
		for C in $(echo "1 2 4"); do
			echo "Number of CORES set to $C"
			for F in $(echo "1 3 5"); do
				echo "Number of FILES set to $F"	
				echo "Running MDR it $n with W$W C$C F$F..."
				./run_mdr.sh $C $F $W

        			mv /tmp/spark-events/* $VIAHOME/main/logs/spark-events/it$n/
				echo "Done!"
				echo ""
			done
        		mv $VIAHOME/main/logs/test* $VIAHOME/main/logs/it$n/
		done
	done

done

