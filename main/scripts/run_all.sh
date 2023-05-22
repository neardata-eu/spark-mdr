#Copyright 2023 Gonzalo Gómez-Sánchez

#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

# ARGUMENTS
CORES=8 #update with number of cores available per machine
FILES=2 #update with the number of files to process
WORKERS=$(wc -l ../nodes/workers.txt)

# START EVERYTHING
./start_container.sh ../nodes/master.txt ../nodes/workers.txt $CORES

# RUN MDR APPLICATION
singularity exec instance://viacontainer python mdr.py -f $FILES -c $CORES -w $WORKERS

# DOWNLOAD RESULTS FROM HDFS
singularity exec instance://viacontainer hdfs dfs -get /output/* ~/via/data/output/

# STOP EVERYTHING
./stop_container.sh ../nodes/master.txt ../nodes/workers.txt

