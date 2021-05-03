#!/usr/bin/python3
from bottle import route, run, template, request, response
from Creation_Certificate import create_certificate
from Verification_Certificate import verify_certificate

@route('/creation', method='POST')
def creation_attestation():

    contenu_identite = request.forms.get('identite')
    contenu_intitule_certification = request.forms.get('intitule_certif')
    result = create_certificate(contenu_identite, contenu_intitule_certification)
    response.set_header('Content-type', 'text/plain')
    print("create certificate successfully")
    return result


@route('/verification', method='POST')
def verification_attestation():
    contenu_image = request.files.get('image')
    contenu_image.save('attestation_a_verifier.png', overwrite=True)
    response.set_header('Content-type', 'text/plain')
    status = verify_certificate()
    print("Verify certificate successfully")
    return status


@route('/fond')
def recuperer_fond():
    response.set_header('Content-type', 'image/png')
    descripteur_fichier = open('attestation.png', 'rb')
    contenu_fichier = descripteur_fichier.read()
    descripteur_fichier.close()
    return contenu_fichier

run(host='0.0.0.0',port=8080,debug=True)
