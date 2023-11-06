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
import time, timeit, sys, getopt, random, os, csv, gzip
import numpy as np
from datetime import datetime

# Date
now = datetime.now()
time = now.strftime("%m%d%y%H%M")


####################
####   PATHS   #####
####################

# PLEASE UPDATE IF NEEDED
# DATA PATHS
DATAPATH = "/home/ubuntu/via/data/input/"
OUTPUTPATH = "/home/ubuntu/via/data/output/"
LOGPATH = "/home/ubuntu/via/main/logs"


####################
#### ARGUMENTS #####
####################

# Date
now = datetime.now()
time = now.strftime("%m%d%y%H%M")

# Default arguments
nf = 1

# Get arguments
arglist = sys.argv[1:]
 
# Options
options = "hf:c:w:"

# Long options
long_options = ["help", "files", "cores", "workers"]

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


# Default values
except getopt.error as err:
    print("ERROR: not enougth arguments. Please, indicate the following arguments:")
    print("-f, --files [int]: use this option followed by an integer to indicate the number of files to be processed.")
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

# Read file with labels and keep only cases/controls
def read_labels(labelspath):
    labels = list()
    with open(labelspath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0 or line_count==1:
                line_count += 1
            else:
                r = row[0].strip(" ")
                labels.append(int(r[len(r)-1]))
                line_count += 1
        print(f'{line_count} labels read.')
        return(labels)

# Read list of files and convert into liest
def file_to_list(filepath):

    with open(filepath, "r") as newfile:
        newfile = newfile.read()
        files = newfile.split("\n")
        return files

# Read sample information and save it into a dict
def read_sample(samplepath):
    sample = dict()
    with gzip.open(samplepath,'rt') as fin:        
        for line in fin:        
            key, val = get_keyval(line)
            sample[key] = val

        return sample

# Cartesian product of 2 arrays. Useful for get all the combinations
def cartesian_product(*arrays):
    la = len(arrays)
    dtype = np.result_type(*arrays)
    arr = np.empty([len(a) for a in arrays] + [la], dtype=dtype)
    for i, a in enumerate(np.ix_(*arrays)):
        arr[...,i] = a
    return arr.reshape(-1, la)

# Save mdrerror to output directory
def save_output(outputpath, mdrerror):
    f = gzip.open(outputpath, 'wt')
    for pair in mdrerror:
        result = list(pair[0]) + pair[1]
        result = [str(x).replace("'","") for x in result] + ["\n"]
        f.write(' '.join(result))
    f.close()

################
##### MAIN #####
################

print("")
print("---------------------")
print("----- STARTING -----")
print("---------------------")
print("")
starttime0 = timeit.default_timer()

# Read patients information
labels = read_labels(DATAPATH + "labels.sample")

# Get np array with cases == 1
npcases = np.array(labels)

# Get np array with controls == 1
npcontrols = np.where((npcases==0)|(npcases==1), npcases^1, npcases)

# Get cases/controls ratio. We will use the number as the high risk/low risk separator
ccratio = npcases.sum(axis=0)/npcontrols.sum(axis=0)

print(f'Ratio of cases/controls is {ccratio}')
print('Creating CV sets...')

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
files = file_to_list(DATAPATH + "listoffiles.txt")
print(f'{len(files)-1} files ready to be processed.')

# Number of files to process
n1 = 0
n2 = 0
total_pairs = 0


print("")
print("------------------------------------------")
print("---------- PROCESSING " + str(nf) + " FILES ----------")
print("------------------------------------------")
print("")

# Compute all the files against all the files
for f1 in files:
    
    print("Loading file " + f1)
    starttimef1 = timeit.default_timer()

    # Read file 1
    sample_1 = read_sample(DATAPATH + "samples/" + f1)

    # Keep only the keys information
    sample_1_ids = list(sample_1.keys())

    # Compute against all the other files
    for f2 in files:

        if f1 <= f2:
            outfile = "mdr_" + f1.replace(".gz","") + "_" + f2.replace(".gz","") + ".gz"
        else:
            continue

        print("Combining it with file " + f2)

        # Read file 2
        sample_2 = read_sample(DATAPATH + "samples/" + f2)

        # Keep only the keys information
        sample_2_ids = list(sample_2.keys())

        # Calculate execution time
        starttimerf2 = timeit.default_timer()

        # Get all the combinations
        cartesiankeys = cartesian_product(np.array(sample_1_ids), np.array(sample_2_ids))

        # Compute MDR
        print("Applying MDR...")
        mdrerror = list()
        for x in cartesiankeys:
            mdrerror.append(apply_mdr_dict(x, sample_1, sample_2))

        total_pairs+=len(mdrerror)
        print(f'MDR applied to {len(mdrerror)} pairs.')

        print(f'Saving MDRERROR to file {outfile}...')
        save_output(OUTPUTPATH + outfile, mdrerror)
        print(f'DONE!')
        print("")

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
    else:
        print("-----------------------------------------")
        print(f'Processing file {n1}.')
        print("")

print("Total time: " + str(timeit.default_timer()-starttime0))
print("Total pairs processed: " + str(total_pairs))


with open(LOGPATH + "/standalone_test_nf.log", 'a') as logfile:
    logfile.write("Number of files: " + str(nf) + "\n")
    logfile.write("Total pairs processed: " + str(total_pairs)+ "\n")
    logfile.write("Total time: " + str(timeit.default_timer()-starttime0)+"\n")
    logfile.write("\n")

