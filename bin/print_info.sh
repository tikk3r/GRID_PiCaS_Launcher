#!/bin/bash





function print_job_info(){

echo "j_info: Run Directory is "${RUNDIR}
echo "PWD is $(pwd)"

echo "j_info: Pipeline Step is ${PIPELINE_STEP}"
echo "j_info:" "INITIALIZATION OF JOB ARGUMENTS"
echo "j_info: jobdir = " ${JOBDIR}
echo "j_info: startSB = " ${STARTSB}
echo "j_info: numSB = " ${NUMSB}
echo "j_info: parset = " ${PARSET}
echo "j_info: OBSID =" ${OBSID}

}



function print_worker_info(){
echo  ""
echo  "-----------------------------------------------------------------------"
echo  "Obtain information for the Worker Node and set the LOFAR environment"
echo  "----------------------------------------------------------------------"

echo "-"
echo "w_info: hostname = "  $HOSTNAME
echo "w_info: homedir = " $HOME
echo "w_info: uname = " $( uname -r )
echo "w_info: Job directory = " $PWD
ls -l $PWD

echo "-"
echo "w_info: WN Architecture is:"
cat /proc/meminfo | grep "MemTotal" |xargs echo "w_info: "
cat /proc/cpuinfo | grep "model name" |xargs echo "w_info: "

#CHECKING FREE DISKSPACE AND FREE MEMORY AT CURRENT TIME
echo ""
echo "w_info: current data and time = " $( date )
echo "w_info: free disk space = "
df -h . 
echo "w_info: free memory " 
free 
freespace=`stat --format "%a*%s/1024^3" -f $TMPDIR|bc`
echo "w_info: Free scratch space = "$freespace"GB"

echo "++++++++++++++++++++++++++++++"
echo "++++++++++++++++++++++++++++++"
mkdir $RUNDIR/Output/versions/

singularity inspect --labels $SIMG |tee  $RUNDIR/Output/versions/singularity.labels
singularity inspect -d $SIMG >> $RUNDIR/Output/versions/singularity.deffile
singularity exec $SIMG /bin/bash -c 'cd /opt/lofar/DPPP/src && git log |head' >> $RUNDIR/Output/versions/DPPP.version
singularity exec  $SIMG /bin/bash -c 'wsclean --version' >>  $RUNDIR/Output/versions/wsclean.version
singularity exec $SIMG /bin/bash -c 'cd /opt/lofar/losoto/build/src && git log |head' >> $RUNDIR/Output/versions/losoto.version
echo ""
}
