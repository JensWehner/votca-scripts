 #!/bin/bash 


Available=$(cat $1 | grep "AVAILABLE" | wc -l)
Assigned=$(cat $1 | grep "ASSIGNED" | wc -l)
Complete=$(cat $1 | grep "COMPELTE" | wc -l)
Failed=$(cat $1 | grep "FAILED" | wc -l)

Total=$((Available + Assigned + Complete + Failed ))
echo "Total number of jobs is ${Total}"
echo "Statefile has ${Available} Available jobs"
echo "Statefile has ${Assigned} Assigned jobs"
echo "Statefile has ${Complete} Complete jobs"
echo "Statefile has ${Failed} Failed jobs"
