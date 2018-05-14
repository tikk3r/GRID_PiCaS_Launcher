#!/bin/bash

function start_profile(){
echo "start tCollector in dryrun mode"
source /cvmfs/softdrive.nl/apmechev/go_packages/init.sh 

echo "" > ${RUNDIR}/pipeline_step
while /bin/true; do 
   monitor_step
done & 


########
#telegraf --config /cvmfs/softdrive.nl/apmechev/go_packages/src/github.com/influxdata/telegraf/telegraf.conf 2>/dev/null &
########
COLL_PID=$!
cd ${RUNDIR}

}


function stop_profile(){
echo "killing tcollector"
kill $COLL_PID

}

function monitor_step(){
export PIPELINE_STEP=$( cat ${RUNDIR}/pipeline_step )

if [ "$PIPELINE_STEP" != "$CURR_STEP"  ]; then
  echo Current Step is $PIPELINE_STEP; 
  export CURR_STEP=$PIPELINE_STEP;
fi; 
sleep 1;

}
