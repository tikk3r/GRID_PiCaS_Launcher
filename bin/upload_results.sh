#!/bin/bash

function upload_error_wrapper(){
## $1 is file, $2 is location; Exits 31 if error; 32 if pools ful; 33 if file exists

globus-url-copy $1 $2  2>upload_error_status
cat upload_error_status

if [[ ! -z $( grep "550 File exists" upload_error_status)  ]]; then
    echo "Upload_error File Exists"
    exit 33
fi

if [[ ! -z $( grep "451 All pools are full" upload_error_status ) ]]; then
   echo "Upload Error: Pools full!"
   exit 32
fi

if [[ ! -z $( grep "550 File not found" upload_error_status )  ]]; then
    echo "Upload_error File cannot be found (folder doesn't exist?)"
    exit 34
fi


if [[ ! -z $( grep "error" upload_error_status )  ]]; then
    echo "Upload Error"
    exit 31
fi
}                     

function upload_results(){
echo "---------------------------------------------------------------------------"
echo "Copy the output from the Worker Node to the Grid Storage Element"
echo "---------------------------------------------------------------------------"

 case "${PIPELINE_STEP}" in
    pref_cal1) upload_results_cal1 ;;
    pref_cal2) upload_results_cal2 ;;
    pref_targ1) upload_results_targ1 ;;
    pref_targ2) upload_results_targ2 ;;
    *) echo ""; echo "Can't find PIPELINE type, will tar and upload everything in the Uploads folder "; echo ""; generic_upload ;;
 esac

}



function generic_upload(){

  cd ${RUNDIR}/Output
  if [ "$(ls -A $PWD)" ]; then
     uberftp -mkdir ${RESULTS_DIR}/${PIPELINE_STEP}/
     uberftp -mkdir ${RESULTS_DIR}/${PIPELINE_STEP}/${OBSID}

     python  ${JOBDIR}/GRID_PiCaS_Launcher/update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'archiving results'   
     tar -cvf results.tar $PWD/* 

     python  ${JOBDIR}/GRID_PiCaS_Launcher/update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'uploading results'   
     echo ""
     echo ""
     echo " Uploading to ${RESULTS_DIR}/${PIPELINE_STEP}/${OBSID}/${OBSID}_${PICAS_USR}_SB${STARTSB}.tar"
     upload_error_wrapper results.tar ${RESULTS_DIR}/${PIPELINE_STEP}/${OBSID}/${OBSID}_${PICAS_USR}_SB${STARTSB}.tar 
   else
    echo "$PWD is Empty"; exit 30; # exit 30 => no files to upload 
  fi
  cd ${RUNDIR}
}

function upload_results_cal1(){
   find ${RUNDIR} -name "instrument" |xargs tar -cvf ${RUNDIR}/Output/instruments_${OBSID}_${STARTSB}.tar  
   find ${RUNDIR} -iname "FIELD" |grep work |xargs tar -rvf ${RUNDIR}/Output/instruments_${OBSID}_${STARTSB}.tar 
   find ${RUNDIR} -iname "ANTENNA" |grep work |xargs tar -rvf ${RUNDIR}/Output/instruments_${OBSID}_${STARTSB}.tar
  
   uberftp -mkdir ${RESULTS_DIR}/${OBSID}
  
   upload_error_wrapper ${RUNDIR}/Output/instruments_${OBSID}_${STARTSB}.tar ${RESULTS_DIR}/${OBSID}/instruments_${OBSID}_SB${STARTSB}.tar 
}

function upload_results_cal2(){
   uberftp -mkdir ${RESULTS_DIR}/${OBSID}
   tar -cvf Output/calib_solutions.tar prefactor/cal_results/*npy prefactor/results/*h5
   upload_error_wrapper Output/calib_solutions.tar ${RESULTS_DIR}/${OBSID}/${OBSID}.tar
 
}


function upload_results_targ1(){

    uberftp -mkdir ${RESULTS_DIR}/${OBSID}
    mv ${RUNDIR}/prefactor/results/L* ${RUNDIR}/Output/
    cp ${PARSET}  $( ls -d ${RUNDIR}/Output/*/)/parset
    ls $( ls -d ${RUNDIR}/Output/*/ )/parset
    cd ${RUNDIR}/Output

    python  ${JOBDIR}/GRID_PiCaS_Launcher/update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'archiving results'      
    tar -cvf results.tar $PWD/* --remove-files

    python  ${JOBDIR}/GRID_PiCaS_Launcher/update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'uploading results'      
    upload_error_wrapper results.tar ${RESULTS_DIR}/${OBSID}/pref_targ1_${OBSID}_AB${A_SBN}_SB${STARTSB}_.tar 
    cd ${RUNDIR}
}

function upload_results_targ2(){

   mv ${RUNDIR}/prefactor/results/L* ${RUNDIR}/Output/
   cp ${PARSET}  $( ls -d ${RUNDIR}/Output/L*/ )/parset
   cd ${RUNDIR}/Output
   python  ${JOBDIR}/GRID_PiCaS_Launcher/update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'archiving results'   
   tar -cvf results.tar -C $PWD/ *

   uberftp -mkdir gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/distrib/SKSP/${OBSID}

   python  ${JOBDIR}/GRID_PiCaS_Launcher/update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'uploading Results'   
   globus-url-copy file:`pwd`/results.tar gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/distrib/SKSP/${OBSID}/GSM_CAL_${OBSID}_ABN_${STARTSB}.tar || { echo "Upload Failed"; exit 31;} # exit 31 => Upload to storage failed 

}


function upload_results_from_token(){

echo ""

}

function upload_with_pipe(){
  cd ${RUNDIR}/Output

  if [ "$(ls -A $PWD)" ]; then
     uberftp -mkdir ${RESULTS_DIR}/${PIPELINE_STEP}/
     uberftp -mkdir ${RESULTS_DIR}/${PIPELINE_STEP}/${OBSID}

     python  ${JOBDIR}/GRID_PiCaS_Launcher/update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'uploading results'
     echo ""
     echo ""
     echo " Uploading to ${RESULTS_DIR}/${PIPELINE_STEP}/${OBSID}/${OBSID}_${PICAS_USR}_SB${STARTSB}.tar"
  
     tar -cvf upload_results.tar ${PWD}/* --remove-files
     globus-url-copy upload_results.tar ${RESULTS_DIR}/${PIPELINE_STEP}/${OBSID}/${OBSID}_${PICAS_USR}_SB${STARTSB}.tar
   else
    echo "$PWD is Empty"; exit 30; # exit 30 => no files to upload 
  fi 
  cd ${RUNDIR}
  rm -rf ${RUNDIR}/Output/*

}

