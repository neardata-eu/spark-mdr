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

# THIS SCRIPTS INIT ALL SERVICES IN ALL NODES AVAILABLE
VIAHOME=$HOME/via

# READ INPUT ARGUMENTS
MASTERFILE=$VIAHOME/main/nodes/master.txt 
WORKERS=$VIAHOME/main/nodes/master.txt
MASTER=$(head -n 1 $MASTERFILE)
CORES=$1


## CREATE SINGULARITY INSTANCES
# Master
echo "Starting instance in master $MASTER"
ssh $MASTER rm -r /tmp/spark/logs /tmp/spark/work /tmp/spark-events
ssh $MASTER mkdir -p /tmp/spark/logs /tmp/spark/work /tmp/spark-events
ssh $MASTER singularity instance start --bind /tmp/spark/logs/:/opt/spark/logs,/tmp/spark/work/:/opt/spark/work,/home/ubuntu/via/singularity/conf/spark/conf:/opt/spark/conf viacontainer.sif viacontainer

## INIT SPARK
# Init master
echo "Starting spark MASTER in $MASTER"
ssh $MASTER singularity exec instance://viacontainer spark-daemon.sh start org.apache.spark.deploy.master.Master 1 --host $MASTER --port 7078 --webui-port 8081; 

# Init workers
echo "Starting spark WORKER in $MASTER"
ssh $MASTER singularity exec instance://viacontainer spark-daemon.sh start org.apache.spark.deploy.worker.Worker 1 --webui-port 8082 $MASTER:7078 --cores $CORES;

