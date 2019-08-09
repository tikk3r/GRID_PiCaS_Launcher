function upload_results(){

results_location=$( python ${JOBDIR}/bin/upload_results.py | tail -1 )

python  ${JOBDIR}/GRID_PiCaS_Launcher/set_token_field.py ${TOKEN} "Results_location" ${results_location} ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD}
}
