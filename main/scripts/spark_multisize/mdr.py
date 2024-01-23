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

# MAIN PYTHON SCRIPT TO APPLY MDR ALGORITHM TO GENOMIC DATASET 

####################
####  IMPORTS  #####
####################

# IMPORTS
import time, pyspark, timeit, sys, getopt, random, os
import numpy as np
from pyspark import SparkContext
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from datetime import datetime

# Date
now = datetime.now()
time = now.strftime("%m%d%y%H%M")

####################
####   PATHS   #####
####################

# SPARK and HDFS master
MASTER = 'bscdc18'
PORT = '7078'

####################
#### ARGUMENTS #####
####################

# Date
now = datetime.now()
time = now.strftime("%m%d%y%H%M")

# Get arguments
arglist = sys.argv[1:]
 
# Options
options = "hf:c:w:s:"

# Long options
long_options = ["help", "files", "cores", "workers", "size"]

try:
    # Parsing argument
    arguments, values = getopt.getopt(arglist, options, long_options)

    # Checking each argument
    for currentArgument, currentValue in arguments:

        # Help
        if currentArgument in ("-h", "--help"):
            print("Please indicate the following values. Otherwise the script won't run.")
            print("-f, --files [int]: use this option followed by an integer to indicate the number of files to be processed.")
            print("-c, --cores [int]: indicate the number of cores per worker.")
            print("-w, --workers [int]: indicate the number of workers available.")
            sys.exit()

        # Set the number of variants to be processed
        elif currentArgument in ("-f", "--files"):
            nf  = int(currentValue)
            print(("Number of files to be processed %s.") % currentValue)

        # Set the number of partitions/slices of the rdd
        elif currentArgument in ("-c", "--cores"):
            CORES = int(currentValue)
            print(("Number of cores set to %s.") % currentValue)

        # Set the number of partitions/slices of the rdd
        elif currentArgument in ("-w", "--workers"):
            WORKERS = int(currentValue)
            print(("Number of workers of spark set to %s.") % currentValue)

        # Set the number of partitions/slices of the rdd
        elif currentArgument in ("-s", "--size"):
            SIZE = int(currentValue)
            print(("Size of files set to %s.") % currentValue)


# Default values
except getopt.error as err:
    print("ERROR: not enougth arguments. Please, indicate the following arguments:")
    print("-f, --files [int]: use this option followed by an integer to indicate the number of files to be processed.")
    print("-c, --cores [int]: indicate the number of cores per worker.")
    print("-w, --workers [int]: indicate the number of workers available.")
    sys.exit()


#####################
##### FUNCTIONS #####
#####################

# Definition of the filter for imputation. We believe the value only if > 0.9
def filter_imputation(x):
    if float(x) >0.9:
        return 1
    return 0

# Vectorize function
imputfilter = np.vectorize(filter_imputation)

# Apply MDR to every SNP-SNP combination reading from a dict
def apply_mdr_dict(x, rd1, rd2):
    key1 = x[0]
    key2 = x[1]
    row1 = rd1[key1]
    row2 = rd2[key2]

    patients = transform_patients((row1,row2))
    
    testerror = get_risk_array(patients)

    return (x[0], x[1]), testerror

# Apply function to every SNP-SNP row to get the interaction matrix
def transform_patients(x):

    #1 - Transform to numpy arrays NO HBASE
    patients1 = np.array(x[0])
    patients2 = np.array(x[1])

    #2 - Reshape as 3 x n patients
    patientsdf1 = np.reshape(patients1, (int(len(patients1)/3),3))
    patientsdf2 = np.reshape(patients2, (int(len(patients2)/3),3))
    
    #3 - Transform to integer
    pt1 = np.matmul(patientsdf1,np.transpose([1,2,3]))*3
    pt2 = np.matmul(patientsdf2,np.transpose([0,1,2]))
    ptcode = pt1-pt2

    return ptcode

# Count number of cases and number of controls for each column and return the high risk combinations.
# Then, use the high risk predictor to obtain the classification and prediction error.
def get_risk_array(patients):

    # Error list
    #trainerror = list()
    testerror = list()
    
    for i in range(5):
        
        # 1 - Get the sets for the iteration
        traindata = trainset[i]
        testdata = testset[i]
        Ntrain = np.sum(traindata)
        Ntest = np.sum(testdata)

        # 2 - Sum only the cases from training set
        cases = patients*npcases.T*traindata.T
        sumcases = count_occurrences(cases)

        # 2 - Sum only the controls
        controls = patients*npcontrols.T*traindata.T
        sumcontrols = count_occurrences(controls)

        # 3 - Get risk array
        #risk = sumcases/sumcontrols
        risk = np.divide(sumcases, sumcontrols, out=np.zeros(sumcases.shape, dtype=float), where=sumcontrols!=0)
        #risk[np.isnan(risk)] = 0

        # 4 - Transform to high risk = 1, low risk = 0
        risk[risk >= ccratio] = 1
        risk[risk < ccratio] = 0

        # 5 - Classify training set
        prediction = apply_risk(patients, risk)

        # Get clasification error
        #trainerror.append((((npcases.T[0] == prediction)*traindata.T)[0]).sum()/Ntrain)

        # 6 - Get clasification error
        cv_testerror = (prediction + npcases.T[0])%2
        cv_testerror = (1-cv_testerror)*testdata.T
        testerror.append((cv_testerror.sum()/Ntest))

    return testerror

# Transform the counts to an array
def count_occurrences(data):
    
    unique, counts = np.unique(data, return_counts=True)
    dtcounts = dict(zip(unique, counts))

    aux = list()
    for i in range(10):
        if i in dtcounts:
            aux.append(dtcounts[i])
        else:
            aux.append(0)
            
    return np.array(aux)

# Apply risk vector to classify the patients
def apply_risk(patients, risk):
    
    prediction = np.zeros(len(patients))
    casevalues = np.where(risk == 1)
    
    for n in casevalues[0][1:]:
        prediction[patients==n] = 1
        
    return prediction.astype(int)


# Transform to key + values
def get_keyval(x):
    aux = x.split()
    key = aux[0] + '-'+ aux[1] +'-'+ aux[2]
    val = imputfilter(aux[5:])
    return (key, val)

# Combine two keys into one
def combine(x):
    k1 = x[0]
    k2 = x[1]
    if k1 == k2:
        return("NONE", 0)
    else:
        if k1 > k2:
            return(k1 + "_" + k2, 0)
        else:
            return(k2 + "_" + k1, 0)


################
##### MAIN #####
################

# PLEASE UPDATE IF NEEDED
# DATA PATHS
DATAPATH = "/home/ubuntu/via/data/input/synth/"
OUTPUTPATH = "/home/ubuntu/via/data/output/"
LOGPATH = "/home/ubuntu/via/main/logs"

print("")
print("---------------------")
print("--- STARTING ---")
print("")
starttime0 = timeit.default_timer()

nPart = CORES

spark = SparkSession \
        .builder \
        .master('spark://'+MASTER+':'+PORT) \
        .appName("MDRspark") \
        .getOrCreate()

sc = spark.sparkContext

print("Connected with spartk")

# Read patients information from HDFS
labels = spark.read.options(header = True, delimiter = " ").csv("file:///" + DATAPATH + "sample.labels")

print("Patients read")

# Keep only case/control information
for h in labels.columns:
    if h != "bin1":
        labels = labels.drop(h)
        
# Filter first non relevant row
labels = labels.filter("bin1!='B'")

# Get np array with cases == 1
npcases = np.array(labels.select("bin1").collect()).astype(int)

# Get np array with controls == 1
npcontrols = np.where((npcases==0)|(npcases==1), npcases^1, npcases)

# Get cases/controls ratio. We will use the number as the high risk/low risk separator
ccratio = npcases.sum(axis=0)/npcontrols.sum(axis=0)
print("Ration cases/controls: " + str(ccratio[0]))

# Create training and test set
Npatients = 1128
Ntrain = Npatients/5*4
Ntest = Npatients/5

# Create training and test set for a 5-CV 
Npatients = 1128
block_size = Npatients/5

trainset = list()
testset = list()

# Create two list with the train and test indexes
for i in range(5):
    nptrain = np.array([np.ones(Npatients, dtype=int)]).T
    nptrain[int(i*block_size):int(i*block_size + block_size)] = 0
    nptest = np.where((nptrain==0)|(nptrain==1), nptrain^1, nptrain)
    
    trainset.append(nptrain)
    testset.append(nptest)

# Read files to be processed
files = sc.textFile("file:///" + DATAPATH + "listoffiles/listoffiles" + str(SIZE) + ".txt").collect()

print("List of files obtained.")

# Number of files to process
n1 = 0
n2 = 0
total_pairs = 0

print("----- RUNNING " + str(nf) + " FILES -----")
print("------------------------------------------")

# Compute all the files against all the files
for f1 in files:
    
    print("Loading file " + f1)
    starttimef1 = timeit.default_timer()

    # Read file 1
    rdd1 = spark.sparkContext.textFile("file:///" + DATAPATH + "samples" + str(SIZE) + "/" + f1)

    # Convert into key-val rdd
    rdd1 = rdd1.map(get_keyval)

    # Save data to HBASE
    rdd1dict = rdd1.collectAsMap()

    # Keep only the keys information
    rdd1 = rdd1.keys()

    # Parallelize dataset
    rdd1 = sc.parallelize(rdd1.collect(), nPart)

    # Compute against all the other files
    for f2 in files:

        if f1 <= f2:
            outfolder = "mdr_" + f1.replace(".gz","") + "_" + f2.replace(".gz","")
        else:
            continue

        print("Combining with file " + f2)

        rdd2 = spark.sparkContext.textFile("file:///" + DATAPATH + "samples" + str(SIZE) + "/" + f2)

        # Convert into key-val rdd
        rdd2 = rdd2.map(get_keyval)

        # Save data to HBASE
        rdd2dict = rdd2.collectAsMap()

        # Keep only the keys information
        rdd2 = rdd2.keys()
        
        # Parallelize dataset
        rdd2 = sc.parallelize(rdd2.collect(), nPart)

        #print("File 2 loaded.")
        #print("Applying MDR...") 

        # Calculate execution time
        starttimerf2 = timeit.default_timer()

        # Create new rdd with tuples of every combination
        cartesiankeys = rdd1.cartesian(rdd2)

        # Compute MDR
        mdrerror = cartesiankeys.map(lambda x: apply_mdr_dict(x, rdd1dict, rdd2dict))
        #print("MDR applied to: " +  str(mdrerror.count()) + " pairs.")
        total_pairs += mdrerror.count()

        #print("Saving data...")
        mdrerror.saveAsTextFile("file:///" + OUTPUTPATH + outfolder)
        #print("Data saved.")
        #print("")

        n2+=1
        if n2==nf:
            n2 = 0
            break

    print("Combined main file " + f1 + " in: " , timeit.default_timer()-starttimef1)
    print("------------------------------------------")
    print ("")

    n1+=1
    if n1==nf:
        break


print("Total time: " + str(timeit.default_timer()-starttime0))
print("Total pairs processed: " + str(total_pairs))


with open(LOGPATH + "/results_" + str(WORKERS) + "_nodes_" + str(size) + "filesizes.log", 'a') as outfile:
    outfile.write("Number of cores: " + str(CORES) + "\n")
    outfile.write("Number of partitions: " + str(nPart) + "\n")
    outfile.write("Number of files: " + str(nf) + "\n")
    outfile.write("Total pairs processed: " + str(total_pairs)+ "\n")
    outfile.write("Total time: " + str(timeit.default_timer()-starttime0)+"\n")
    outfile.write("\n")

