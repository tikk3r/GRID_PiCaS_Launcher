#!/bin/bash

function cleanup(){                                                                                                                               

echo ""
python  $"{JOBDIR}"/GRID_PiCaS_Launcher/update_token_status.py $"{PICAS_DB}" $"{PICAS_USR}" $"{PICAS_USR_PWD}" $"{TOKEN}" 'cleaning up'
echo ""
echo "copy logs to the Job home directory and clean temp files in scratch"
cp out* $"{JOBDIR}"
#cp pngs.tar.gz $"{JOBDIR}"
cd $"{JOBDIR}" || exit 4 # Exit 4-> JOBDIR doesn't exist

if [[ $(hostname -s) == 'f18-01.gina.sara.nl' ||    $(hostname -s) == 'loui.grid.surfsara.nl' ]]; then
    echo "Keeping RUNDIR"
    return 0
fi

echo "removing RunDir"
rm -rf $"{RUNDIR}"



#ls -l $"{RUNDIR}""
echo ""
echo "listing final files in Job directory"
ls -allh $"PWD"
echo ""
du -hs $"PWD"
}

