#!/bin/bash

if [ $# == 0 ]; then
    echo "Usage: [param1] [param2] [param3]"
    echo "* param1: <option: create, verify>"
    echo "--if option is create--"
    echo "* param2: <identite>"
    echo "* param3: <intitule_certif>"
    echo "--if option is verify"
    echo "* param2: <path to image>"
    echo "* param3: no longer need"
    echo "--if option is download"
    echo "* param2: <image name>"
    echo "* param3: no longer need"
fi

if [[ $1 == "create" ]]
then
	curl -X POST -d 'identite='"$2" -d 'intitule_certif='"$3" --cacert CA/ecc.ca.cert.pem https://localhost:9000/creation
fi

if [[ $1 == "verify" ]]
then
	curl -v -F image=@"$2" --cacert CA/ecc.ca.cert.pem https://localhost:9000/verification
fi

if [[ $1 == "download" ]] 
then
	curl -v -o "$2" --cacert CA/ecc.ca.cert.pem https://localhost:9000/fond
fi
