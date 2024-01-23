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

VIAHOME=$HOME/via

# ARGUMENTS
CORES=$1
FILES=$2
N_WORKERS=$3

# First, we copy the number of workers we want to the workers file
WORKERS=$(wc -l $VIAHOME/main/nodes/master.txt)

# START EVERYTHING
./start_container.sh $CORES

nohup vmstat 5 600 > memory_st_c$1_f$2.dat &

# RUN MDR APPLICATION
perf stat -o pout.txt singularity exec instance://viacontainer python mdr.py -f $FILES -c $CORES -w $N_WORKERS

# STOP EVERYTHING
./stop_container.sh

