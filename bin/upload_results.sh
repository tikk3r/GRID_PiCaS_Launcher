#!/bin/bash

function upload_results(){
python ${JOBDIR}/GRID_PiCaS_Launcher/update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'uploading_results'
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
     uberftp -mkdir ${RESULTS_DIR}/${PIPELINE_STEP}/${OBSID}
     tar -cvf results.tar $PWD/* 
     echo ""
     echo ""
     echo " Uploading to ${RESULTS_DIR}/${PIPELINE_STEP}/${OBSID}/${OBSID}_${PICAS_USR}_SB${STARTSB}.tar"
     globus-url-copy results.tar ${RESULTS_DIR}/${PIPELINE_STEP}/${OBSID}/${OBSID}_${PICAS_USR}_SB${STARTSB}.tar || { echo "Upload Failed"; exit 31;} # exit 31 => Upload to storage failed
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

 globus-url-copy ${RUNDIR}/Output/instruments_${OBSID}_${STARTSB}.tar ${RESULTS_DIR}/${OBSID}/instruments_${OBSID}_${STARTSB}.tar  || { echo "Upload Failed"; exit 31;} # exit 31 => Upload to storage failed   
}

function upload_results_cal2(){

         globus-url-copy file:`pwd`/calib_solutions.tar gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/prefactor/cal_sols/${OBSID}_solutions.tar || { echo "Upload Failed"; exit 31;} # exit 31 => Upload to storage failed
        wait
}


function upload_results_targ1(){

uberftp -mkdir gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/prefactor/SKSP/${OBSID}
globus-url-copy file:`pwd`/results.tar.gz gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/prefactor/SKSP/${OBSID}/t1_${OBSID}_AB${A_SBN}_SB${STARTSB}_.tar.gz || { echo "Upload Failed"; exit 31;} # exit 31 => Upload to storage failed

}

function upload_results_targ2(){

   uberftp -mkdir gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/distrib/SKSP/${OBSID}
   globus-url-copy file:`pwd`/results.tar.gz gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/distrib/SKSP/${OBSID}/GSM_CAL_${OBSID}_ABN_${STARTSB}.tar.gz || { echo "Upload Failed"; exit 31;} # exit 31 => Upload to storage failed 
    wait
}


function upload_results_from_token(){

echo ""

}
