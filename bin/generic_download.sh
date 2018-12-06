#!/bin/bash

#First argument is file, second argument is $PIPELINE




function dl_generic(){
    echo "Initiating generic download"
   python  ${JOBDIR}/GRID_PiCaS_Launcher/update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'downloading'
    if [[ ! -z $( cat $1 | grep juelich )  ]]; then 
     sed 's?srm://lofar-srm.fz-juelich.de:8443?gsiftp://lofar-gridftp.fz-juelich.de:2811?g' $1 | xargs -I{} globus-url-copy -rst -st 30 -fast -v {} $PWD/Input/ || { echo 'downloading failed' ; exit 21; }
   fi

   if [[ ! -z $( cat $1 | grep sara )  ]]; then
     sed 's?srm://srm.grid.sara.nl:8443?gsiftp://gridftp.grid.sara.nl:2811?g' $1 | xargs -I{} globus-url-copy -rst -st 30 -fast -v {} $PWD/Input/ || { echo 'downloading failed' ; exit 21; }
   fi
   
   if [[ ! -z $( cat $1 | grep psnc )  ]]; then
     sed 's?srm://lta-head.lofar.psnc.pl:8443?gsiftp://gridftp.lofar.psnc.pl:2811?g' $1 | xargs -I{} globus-url-copy -rst  -st 30 -fast -v {} $PWD/Input/ || { echo 'downloading failed' ; exit 21; }
   fi
   
   wait
   OLD_P=$PWD 
   cd ${RUNDIR}/Input
   python  ${JOBDIR}/GRID_PiCaS_Launcher/update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'extracting'              

   for i in `ls *tar`; do tar -xvf $i && rm -rf $i; done
   for i in `ls *gz`; do tar -zxvf $i && rm -rf $i; done
   cd ${RUNDIR}

   echo "Download Done!"

}



if [ ! -n "$(type -t download_files )"   ] && [ ! "$(type -t download_files )" = function   ]; then

    echo "Defining generic download"
    function download_files(){
        echo "Generic download of files since Sanbdox doesn't have bin/download.sh"
        dl_generic $1                                                              
        cd ${RUNDIR}/Input
        find . -type d  -name "*.ms" -exec mv {} ${RUNDIR}/Input \;
        find . -type d  -name "*.MS" -exec mv {} ${RUNDIR}/Input \;
        echo "Input directory conents:"
        echo ""
        ls ${RUNDIR}/Input
        cd ${RUNDIR}

}
fi


