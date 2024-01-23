VIAHOME=$HOME/via

for n in $(echo "1"); do
#for n in $(echo "1 2 3"); do
	echo "-----------------------------"
	echo "Running iteration $n of MDR..."
	echo "-----------------------------"
	mkdir $VIAHOME/main/logs/it$n $VIAHOME/main/logs/spark-events/it$n
	for W in $(echo "3"); do
	#for W in $(echo "1 2 3"); do
		echo "Number of WORKERS set to $W"
		for C in $(echo "4"); do
		#for C in $(echo "1 2 4"); do
			echo "Number of CORES set to $C"
			for F in $(echo "5"); do
			#for F in $(echo "1 3 5"); do
				echo "Number of FILES set to $F"	
				echo "Running MDR it $n with W$W C$C F$F..."
				./run_mdr.sh $C $F $W
                                rm -r /home/ubuntu/via/data/output/* 
				for event in /tmp/spark-events/* ; do mv -- "$event" "$VIAHOME/main/logs/spark-events/it$n/x86_app_I${n}_W${W}_C${C}_F${F}" ; done
				echo "Done!"
				echo ""
			done
        		mv $VIAHOME/main/logs/test* $VIAHOME/main/logs/it$n/
		done
	done

done

