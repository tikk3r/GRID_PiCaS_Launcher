#!/bin/bash

function start_profile(){
echo "start telegraf in prod mode"
source /cvmfs/softdrive.nl/apmechev/go_packages/init.sh 
#Used to only profile processes with the current session ID
export CURRENT_SESSION=$$

echo "" > ${RUNDIR}/pipeline_step
########
#telegraf --config /cvmfs/softdrive.nl/apmechev/go_packages/src/github.com/influxdata/telegraf/telegraf.conf 2>/dev/null &
########
#COLL_PID=$!

monitor_loop &

cd ${RUNDIR}

}


function stop_profile(){
echo "killing tcollector"
kill $COLL_PID
killall -9 telegraf
}

function monitor_step(){
 export PIPELINE_SUB_STEP="${PIPELINE_STEP}":"$( cat ${RUNDIR}/pipeline_step )"
  
  if [ "$PIPELINE_SUB_STEP" != "$CURR_STEP"  ]; then
      if [ ! -z $( echo $COLL_PID ) ]; then
          kill $COLL_PID;
          killall telegraf;
      fi
      launch_telegraf &
      echo "Launching TELEGRAF for pipeline step $PIPELINE_SUB_STEP" 
      export COLL_PID=$!
      export CURR_STEP=$PIPELINE_SUB_STEP;
  fi; 
 sleep 1;
}

function monitor_loop(){
 while /bin/true; do
       monitor_step
 done  
}

function launch_telegraf(){
   telegraf --config /cvmfs/softdrive.nl/apmechev/go_packages/src/github.com/influxdata/telegraf/telegraf.conf 2>/dev/null 
}
