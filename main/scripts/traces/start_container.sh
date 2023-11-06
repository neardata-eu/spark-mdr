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
WORKERS=$VIAHOME/main/nodes/workers.txt
MASTER=$(head -n 1 $MASTERFILE)
#CORES=$1
CORES=8

## CREATE SINGULARITY INSTANCES
# Master
echo "Starting instance in master $MASTER"
ssh $MASTER mkdir -p /tmp/spark/logs /tmp/spark/work /tmp/spark-events
ssh $MASTER singularity instance start --bind /tmp/spark/logs/:/opt/spark/logs,/tmp/spark/work/:/opt/spark/work,/home/ubuntu/via/singularity/conf/spark/conf:/opt/spark/conf viacontainer.sif viacontainer

# Workers
while read -u10 WK; do
	echo "Starting instance in worker $WK"
        ssh $WK rm -r /tmp/*
	ssh $WK mkdir -p /tmp/hdfs/namenode
        ssh $WK mkdir -p /tmp/hdfs/datanode
        ssh $WK mkdir -p /tmp/spark/logs /tmp/spark/work /tmp/spark-events
	ssh $WK singularity instance start --bind /tmp/spark/logs/:/opt/spark/logs,/tmp/spark/work/:/opt/spark/work,/home/ubuntu/via/singularity/conf/spark/conf:/opt/spark/conf viacontainer.sif viacontainer
done 10< $WORKERS

# INIT ZOOKEEPER
echo "Starting Zookeeper"
./zookeeper_start.sh $VIAHOME/main/nodes/master.txt $VIAHOME/main/nodes/workers.txt

## INIT SPARK & HDFS
# Init master
echo "Starting spark and HDFS in MASTER $MASTER"
ssh $MASTER singularity exec instance://viacontainer spark-daemon.sh start org.apache.spark.deploy.master.Master 1 --host $MASTER --port 7078 --webui-port 8081
ssh $MASTER echo 'Y' | singularity exec instance://viacontainer hdfs namenode -format
ssh $MASTER singularity exec instance://viacontainer hdfs --daemon start namenode
ssh $MASTER singularity exec instance://viacontainer yarn --daemon start resourcemanager

# Init workers
n=1
while read -u10 WK; do
        port=$((8081+$n))
	echo "Starting spark and HDFS in WORKER $WK"
        ssh $WK singularity exec instance://viacontainer spark-daemon.sh start org.apache.spark.deploy.worker.Worker $n --webui-port $port $MASTER:7078 --cores $CORES;
        ssh $WK singularity exec instance://viacontainer hdfs --daemon start datanode
        ssh $WK singularity exec instance://viacontainer yarn --daemon start nodemanager
	n=$(($n+1))
done 10< $WORKERS

# Upload files to HDFS
echo "Uploading files to HDFS"
singularity exec instance://viacontainer hdfs dfs -mkdir /input
singularity exec instance://viacontainer hdfs dfs -mkdir /output
singularity exec instance://viacontainer hdfs dfs -put ~/via/data/input/samples/* /input
singularity exec instance://viacontainer hdfs dfs -put ~/via/data/input/labels.sample /input
singularity exec instance://viacontainer hdfs dfs -put ~/via/data/input/listoffiles.txt /input

echo "Checking HDFS directory"
singularity exec instance://viacontainer hdfs dfs -ls /input/

