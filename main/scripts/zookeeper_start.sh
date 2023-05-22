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

# THIS SCRIPT STARTS ZOOKEEPER IN ALL NODES

# Set Master
MASTER=$(head -n 1 $1)
WORKERS=$2

#MASTER
n=1
ssh $MASTER mkdir -p /tmp/zookeeper
echo $n > /tmp/zookeeper/myid1
scp /tmp/zookeeper/myid1 $MASTER:/tmp/zookeeper/myid
ssh $MASTER singularity exec instance://viacontainer zkServer.sh start

#WORKERS
n=2
while read -u10 WK; do
	ssh $WK mkdir -p /tmp/zookeeper
	echo $n > /tmp/zookeeper/myid1
	scp /tmp/zookeeper/myid1 $WK:/tmp/zookeeper/myid
	ssh $WK singularity exec instance://viacontainer zkServer.sh start
        n=$(($n+1))
done 10< $WORKERS

# View Zookeeper status
ssh bscdc18 singularity exec instance://viacontainer zkServer.sh status
ssh bscdc19 singularity exec instance://viacontainer zkServer.sh status
ssh bscdc20 singularity exec instance://viacontainer zkServer.sh status
