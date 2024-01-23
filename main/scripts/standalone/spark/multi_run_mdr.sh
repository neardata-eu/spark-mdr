VIAHOME=$HOME/via

for W in $(echo "1"); do
#for W in $(echo "1 2 3"); do
	echo "Number of WORKERS set to $W"
	#for C in $(echo "4"); do
	for C in $(echo "4"); do
		echo "Number of CORES set to $C"
		#for F in $(echo "5"); do
		for F in $(echo "5"); do
			echo "Number of FILES set to $F"	
			echo "Running MDR it $n with W$W C$C F$F..."
			./run_mdr.sh $C $F $W
                        rm -r /home/ubuntu/via/data/output/* 
			for event in /tmp/spark-events/* ; do mv -- "$event" "$VIAHOME/main/logs/spark-events/x86st_app_I${n}_W${W}_C${C}_F${F}" ; done
			echo "Done!"
			echo ""
		done
	done

done

