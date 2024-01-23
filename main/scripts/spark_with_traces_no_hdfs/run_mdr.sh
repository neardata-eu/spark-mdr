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

# DEFAULT - comment if multirun
#CORES=8 #update with number of cores available per machine
#FILES=1 #update with the number of files to process
#N_WORKERS=2

# First, we copy the number of workers we want to the workers file
head -$N_WORKERS $VIAHOME/main/nodes/workers_list.txt > $VIAHOME/main/nodes/workers.txt
WORKERS=$(wc -l $VIAHOME/main/nodes/workers.txt)

# START EVERYTHING
./start_container.sh $CORES

# RUN MDR APPLICATION
singularity exec instance://viacontainer python -m cProfile -o profile/profile_x86_f${FILES}_c${CORES}_w${N_WORKERS}.pyprof mdr.py -f $FILES -c $CORES -w $N_WORKERS

# STOP EVERYTHING
./stop_container.sh

