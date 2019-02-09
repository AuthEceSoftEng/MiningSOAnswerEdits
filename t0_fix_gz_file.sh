# Processing file
echo $1

# Set variables
origfilename=$1                         # file.csv.gz
csvfilename="${origfilename%.*}"        # file.csv
tarfilename="${csvfilename}.tar"        # file.csv.tar

# Perform operations
gunzip -c $1 > $tarfilename
gunzip -c $tarfilename > $csvfilename
rm $origfilename
gzip -c $csvfilename > $origfilename

# Clean up
rm $csvfilename
rm $tarfilename
