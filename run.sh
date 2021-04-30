#! /bin/bash

CA_FOLDER="CA"
TS_FOLDER="ts"
IMG_FOLDER="images"
PATH_TO_FOND="images/fond_attestation.png"
PATH_TO_CA_KEY="CA/ecc.ca.key.pem"
PATH_TO_CA_CERT="CA/ecc.ca.cert.pem"
PATH_TO_SERVER_KEY="CA/ecc.server.key.pem"
PATH_TO_SERVER_CERT="CA/ecc.server.cert.pem"
PATH_TO_SERVER_CSR="CA/ecc.server.csr.pem"
PATH_TO_SERVER_PUBKEY="CA/ecc.server.pubkey.pem"
PATH_TO_BUNDLE_SERVER="CA/bundle_server.pem"
PATH_TO_TSA_CRT="ts/tsa.crt"
PATH_TO_TS_CA_CERT="ts/cacert.pem"

SERVER_NAME="localhost"

if [ ! -d "$IMG_FOLDER" ]; then
	mkdir $IMG_FOLDER
fi

if [ ! -f "$PATH_TO_FOND" ]; then
	cd $IMG_FOLDER
	wget http://p-fb.net/fileadmin/fond_attestation.png
	cd ../
fi

if [ ! -d "$CA_FOLDER" ]; then
	mkdir $CA_FOLDER
fi

if [ ! -d "$TS_FOLDER" ]; then
	mkdir $TS_FOLDER
fi

if [ ! -f "$PATH_TO_TSA_CRT" ]; then
	cd $TS_FOLDER
	wget https://freetsa.org/files/tsa.crt
	cd ../
fi

if [ ! -f "$PATH_TO_TS_CA_CERT" ]; then
	cd $TS_FOLDER
	wget https://freetsa.org/files/cacert.pem
	cd ../
fi

echo "Generate CA key..."
openssl ecparam -out $PATH_TO_CA_KEY -name prime256v1 -genkey
echo "Generate CA certificate..."
openssl req -config <(printf "[req]\ndistinguished_name=dn\n[dn]\n[ext]\nbasicConstraints=CA:TRUE") \
	-new -nodes -subj "/C=FR/L=Limoges/O=CRYPTIS/OU=SecuTIC/CN=ACSECUTIC" \
	-x509 -extensions ext -sha256 -key $PATH_TO_CA_KEY -text -out $PATH_TO_CA_CERT

echo "Generate server key..."
openssl ecparam -out $PATH_TO_SERVER_KEY -name prime256v1 -genkey
echo "Generate server certificate signing request..."
openssl req -config <(printf "[req]\ndistinguished_name=dn\n[dn]\n[ext]\nbasicConstraints=CA:FALSE") \
	-new -subj "/C=FR/L=Limoges/O=CRYPTIS/OU=SecuTIC/CN=$SERVER_NAME" \
	-reqexts ext -sha256 -key $PATH_TO_SERVER_KEY -text -out $PATH_TO_SERVER_CSR
echo "Generate server certificate..."
openssl x509 -req -days 3650 -CA $PATH_TO_CA_CERT -CAkey $PATH_TO_CA_KEY \
	-CAcreateserial -extfile <(printf "basicConstraints=critical,CA:FALSE") \
	-in $PATH_TO_SERVER_CSR -text -out $PATH_TO_SERVER_CERT
echo "Extract server public key from certificate..."
openssl x509 -pubkey -noout -in $PATH_TO_SERVER_CERT > $PATH_TO_SERVER_PUBKEY

echo "Generate bunlde server..."
cat $PATH_TO_SERVER_KEY $PATH_TO_SERVER_CERT > $PATH_TO_BUNDLE_SERVER
