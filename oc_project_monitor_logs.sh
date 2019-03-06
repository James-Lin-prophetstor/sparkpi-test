# split logs by Docker UID
FILE=$(ls |grep 'pod_in_'|grep '.log')
mkdir cc
for UID in `cat $FILE  |awk  '{print $3}' `
do 
    grep $UID $FILE >> cc/$UID
done

for X in $(ls cc) ;
do
    grep $X $FILE >> $X.txt
done