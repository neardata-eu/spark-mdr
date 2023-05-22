# DATA STRUCTURE

Here you must add your data. For privacy policies, we can not provide real data so here you can find a small synthethic dataset for testing with the esencial information. Information not used by the application is substituted by $, but not deleted in order to adapt to real data format.

# /samples

Change this folder for the folder with your samples information. The information must be compressed in a .gz files. Here you can find a sample line of a file:

22 chr2218429957 18429957 G A 1 0 0 1 0 0 ... 

where:
22: chromosome number
chr2218429957: chromosome number + rsid
18429957: rsid
G: reference allele
A: alternate allele
1: binary code for patient 1 being AA
0: binary code for patient 1 being Aa
0: binary code for patient 1 being aa
0: binary code for patient 2 being AA
1: binary code for patient 2 being Aa
0: binary code for patient 2 being aa
...: 3 column groups until complete all the patients of your cohort

# labels.sample

Change this file for your own samples information file. Here is the proposed structure to be included:

ID_1 ID_2 missing heterozygosity PC1 PC2 PC3 PC4 PC5 PC6 PC7 BMI_avg sex bin1

Where bin1 is a binary that is 1 for 'case' and 0 for 'control'. The rest of information is not used for the analysis.

