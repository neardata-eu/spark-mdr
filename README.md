# VIA

## Project description
Variant Interaction Analysis (VIA) is an application for identifying genomic variant interactions related with complex diseases. It uses Multifactor Dimensionality Dimension (MDR), a non-parametric statistical method for detecting and characterizing nonlinear interactions. It runs in a singularity container using Apache Spark for distributing the work, Hadoop File System for distributing the data and Apache ZooKeeper for synchronization. It is coded in Python.

This work is pending to be publish.

## Usage
### Build the singularity image
For building the singularity image, run the following commands
cd singularity
sudo singularity build viacontainer.sif viacontainer.def
mv viacontainer.sif ~/viacontainer.sif

then, make sure you copy the image to every working node.

### Running the experiments
For running the application, run the following commands:
cd ~/via/main/scripts
./run_all.sh

## Requirements
Please use Singularity Version 3.6.4 or newer.

## License
Copyright 2023 Gonzalo Gómez-Sánchez

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

