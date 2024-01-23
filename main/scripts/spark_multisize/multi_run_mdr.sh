VIAHOME=$HOME/via

for size in $(echo "1 2 5 10 20 50 75 100 200 500"); do
	echo "----------------------------------------"
	echo "Running files with size $size of MDR..."
	echo "----------------------------------------"
	mkdir $VIAHOME/main/logs/s$size $VIAHOME/main/logs/spark-events/s$size
	for W in $(echo "3"); do
	#for W in $(echo "1 2 3"); do
		echo "Number of WORKERS set to $W"
		for C in $(echo "4"); do
		#for C in $(echo "1 2 4"); do
			echo "Number of CORES set to $C"
			for F in $(echo "2"); do
			#for F in $(echo "1 3 5"); do
				echo "Number of FILES set to $F"	
				echo "Running MDR with size=$size, worker=$W, cores=$C, files=$F."
				./run_mdr.sh $C $F $W $size
                                rm -r /home/ubuntu/via/data/output/* 
				for event in /tmp/spark-events/* ; do mv -- "$event" "$VIAHOME/main/logs/spark-events/size$size/x86_app_I${n}_W${W}_C${C}_F${F}" ; done
				echo "Done!"
				echo ""
			done
        		mv $VIAHOME/main/logs/test* $VIAHOME/main/logs/size$size/
		done
	done

done

