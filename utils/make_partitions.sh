FILE=/home/ubuntu/via/data/input/NuGENE_chr22_repaired.gz
SUFFIX=chr0_synth
OUTPATH=/home/ubuntu/via/data/input/samples

OUTFILE=${FILE%.*}
echo $OUTFILE

mkdir -p $OUTPATH/

gzip -d -k $FILE
split -l 100 -d -a 4 $OUTFILE $OUTPATH/$SUFFIX
gzip $OUTPATH/*

# Create list of partitions
ls $OUTPATH/ > $OUTPATH/listoffiles.txt

