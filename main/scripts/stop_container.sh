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

# THIS SCRIPT STOP ALL SERVICES IN ALL NODES

# STOP INSTANCES
# Stop Master
while read -u10 WORKER; do
	echo "Stopping instance in node" $WORKER
        ssh $WORKER singularity instance stop viacontainer
done 10< $1

# Stop Workers
while read -u10 WORKER; do
	echo "Stopping instance in node" $WORKER
        ssh $WORKER singularity instance stop viacontainer
done 10< $2

