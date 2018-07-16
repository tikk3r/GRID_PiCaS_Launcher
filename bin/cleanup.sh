function cleanup(){

echo ""
python  ${JOBDIR}/GRID_PiCaS_Launcher/update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'cleaning up'  
echo ""
echo "copy logs to the Job home directory and clean temp files in scratch"
cp out* ${JOBDIR}
#cp pngs.tar.gz ${JOBDIR}
cd ${JOBDIR}

if [[ $(hostname -s) != 'f18-01' ]]; then
    echo "removing RunDir"
    rm -rf ${RUNDIR}
fi
#ls -l ${RUNDIR}
echo ""
echo "listing final files in Job directory"
ls -allh $PWD
echo ""
du -hs $PWD
}
