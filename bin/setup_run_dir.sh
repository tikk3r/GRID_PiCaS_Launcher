
function setup_sara_dir(){

export PYTHONPATH=${PWD}:$PYTHONPATH
source /cvmfs/softdrive.nl/lofar_sw/env/current_dysco.sh 

cp *parset $1               2>/dev/null
tlog info "copying $(*.parset) to $1"
cp -r  $PWD/prefactor/ $1   2>/dev/null
#TODO: Make this block just a git pull?
cp *py $1   

cp srm.txt $1 #this is a fallthrough by taking the srm from the token not from the sandbox!

cp ${PARSET} $1
cp ${SCRIPT} $1             2>/dev/null

cp -r $PWD/ddf-pipeline $1  2>/dev/null
cp -r $PWD/skymodels $1     2>/dev/null
cp -r $PWD/tools $1         2>/dev/null
cp pipeline.cfg $1          2>/dev/null
cp sing_pipeline.cfg $1          2>/dev/null

cd ${RUNDIR}
touch pipeline_status

mkdir -p Input
mkdir -p Output
}

function setup_run_dir(){
 case "$( hostname -f )" in
    *sara*) export RUNDIR=`mktemp -d -p ${JOBDIR}`; setup_sara_dir ${RUNDIR} ;;
    *novalocal*) export RUNDIR=`mktemp -d -p ${JOBDIR}`; setup_sara_dir ${RUNDIR} ;;
    *leiden*) setup_leiden_dir ;;
    node[0-9]*) export RUNDIR=`mktemp --directory --tmpdir=/data/lofar/grid_jobs`; setup_sara_dir ${RUNDIR} ;;
    *) echo "Can't find host in list of supported clusters"; exit 11;;
 esac
}

