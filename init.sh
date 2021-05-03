#!/bin/bash

PATH_TO_CA_KEY="CA/ecc.ca.key.pem"
PATH_TO_CA_CERT="CA/ecc.ca.cert.pem"
PATH_TO_SERVER_KEY="CA/ecc.server.key.pem"
PATH_TO_SERVER_CERT="CA/ecc.server.cert.pem"
PATH_TO_SERVER_CSR="CA/ecc.server.csr.pem"
PATH_TO_SERVER_PUBKEY="CA/ecc.server.pubkey.pem"
PATH_TO_BUNDLE_SERVER="CA/bundle_server.pem"

if [[ ! -d "images" ]]
then
	mkdir images
fi

if [[ ! -d "CA" ]]
then
	mkdir CA 
fi

if [[ ! -d "ts" ]]
then
	mkdir ts 
fi

if [[ ! -f "images/fond_attestation.png" ]]
then
	wget -P images http://p-fb.net/fileadmin/fond_attestation.png
fi

if [[ ! -f "ts/tsa.crt" ]]
then
	wget -P ts https://freetsa.org/files/tsa.crt
fi

if [[ ! -f "ts/cacert.pem" ]]
then
	wget https://freetsa.org/files/cacert.pem -P ts
fi

openssl ecparam -out $PATH_TO_CA_KEY -name prime256v1 -genkey

openssl req -config <(printf "[req]\ndistinguished_name=dn\n[dn]\n[ext]\nbasicConstraints=CA:TRUE") \
	-new -nodes -subj "/C=FR/L=Limoges/O=CRYPTIS/OU=SecuTIC/CN=CertifPlus" \
	-x509 -extensions ext -sha256 -key $PATH_TO_CA_KEY -text -out $PATH_TO_CA_CERT

openssl ecparam -out $PATH_TO_SERVER_KEY -name prime256v1 -genkey

openssl req -config <(printf "[req]\ndistinguished_name=dn\n[dn]\n[ext]\nbasicConstraints=CA:FALSE") \
	-new -subj "/C=FR/L=Limoges/O=CRYPTIS/OU=SecuTIC/CN=localhost" \
	-reqexts ext -sha256 -key $PATH_TO_SERVER_KEY -text -out $PATH_TO_SERVER_CSR

openssl x509 -req -days 3650 -CA $PATH_TO_CA_CERT -CAkey $PATH_TO_CA_KEY \
	-CAcreateserial -extfile <(printf "basicConstraints=critical,CA:FALSE") \
	-in $PATH_TO_SERVER_CSR -text -out $PATH_TO_SERVER_CERT

openssl x509 -pubkey -noout -in $PATH_TO_SERVER_CERT > $PATH_TO_SERVER_PUBKEY

openssl x509 -pubkey -in $PATH_TO_CA_CERT > CA/ecc.ca.pubkey.pem

cat $PATH_TO_SERVER_KEY $PATH_TO_SERVER_CERT > $PATH_TO_BUNDLE_SERVER

# Option 
# openssl ec -in CA/ecc.ca.key.pem -out CA/enc.ecc.ca.key.pem -aes256
