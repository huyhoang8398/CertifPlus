import subprocess
import base64
from typing import Protocol
import qrcode
from PIL import Image
from subprocess import Popen, PIPE
from Creation_Stegano import cacher


def create_qrcode(data):  #data is the signature
    nom_fichier = "./images/qrcode.png"
    qr = qrcode.make(data)
    qr.save(nom_fichier, scale=2)


def generate_text_image(identify,
                        institute):  # Generate text for certificate titile
    texte_ligne = "Attestation de reussite|delivree a {} {}".format(
        identify, institute)
    print(texte_ligne)
    Process = subprocess.Popen(
        'curl -o texte.png "http://chart.apis.google.com/chart" --data-urlencode "chst=d_text_outline" --data-urlencode "chld=000000|56|h|FFFFFF|b|{}"'
        .format(texte_ligne),
        shell=True,
        stdout=subprocess.PIPE)

    (output, error) = Process.communicate()
    if Process.returncode == 0:
        print("Create text image")
        return True
    else:
        return False


def combine_image():
    Process = subprocess.Popen([
        'mogrify -resize 1000x600 texte.png && composite -gravity center texte.png ./images/fond_attestation.png combinaison.png',
    ],
                               shell=True,
                               stdout=subprocess.PIPE)

    (output, error) = Process.communicate()
    if Process.returncode == 0:
        print("Composite image to background...")
        return True
    else:
        return False


def combine_qrcode():
    Process = subprocess.Popen([
        'mogrify -resize 210x210 ./images/qrcode.png && composite -geometry +1418+934 ./images/qrcode.png combinaison.png attestation.png',
    ],
                               shell=True,
                               stdout=subprocess.PIPE)

    (output, error) = Process.communicate()
    if Process.returncode == 0:
        print("Composite qrcode to background...")
        return True
    else:
        return False


def create_signature(info):
    data = make_full_char_info(info)
    file = open("./CA/info.txt", "w")
    file.write(data)
    file.close()

    Process = subprocess.Popen([
        "openssl dgst -sha256 -sign CA/enc.ecc.ca.key.pem ./CA/info.txt > ./CA/signature.sig"
    ],
                               shell=True,
                               stdout=subprocess.PIPE)

    (output, error) = Process.communicate()

    if Process.returncode == 0:
        print("create signature")
        return True
    else:
        print("-------------------\nWrong password")
        print("\nCreate certificate failed")
        return False


def create_timespamp(signature):

    ProcessTSQ = subprocess.Popen([
        "openssl ts -query -data {} -no_nonce -sha512 -cert -out ./ts/ts_query.tsq"
        .format(signature)
    ],
                                  shell=True,
                                  stdout=subprocess.PIPE)

    (output, error) = ProcessTSQ.communicate()

    if ProcessTSQ.returncode == 0:
        print("Create timestamp-query")
    else:
        print("Create timestamp-query failed")

    ProcessTSR = subprocess.Popen([
        'curl -H "Content-Type: application/timestamp-query" --data-binary "@./ts/ts_query.tsq" https://freetsa.org/tsr > ./ts/ts_respond.tsr'
    ],
                                  shell=True,
                                  stdout=subprocess.PIPE)
    (output, error) = ProcessTSR.communicate()

    if ProcessTSR.returncode == 0:
        print("create timestamp ts_respond")
        return True
    else:
        return False


def make_full_char_info(data):  # generate 64 character
    if (len(data) < 64):
        gaps = 64 - len(data)
        data = data + '\x01' * gaps
        return data
    return data


def bin_to_base64(file):
    f = open(file, "rb")
    data = f.read()
    f.close()
    return base64.b64encode(data).decode('ascii')


def create_certificate(nomEtPrenom, institute):
    signature = nomEtPrenom + institute
    print(signature)
    if (create_signature(signature)):
        create_timespamp("./CA/signature.sig")
        signatureAscii = bin_to_base64("./CA/signature.sig")
        f = open("./CA/info.txt", "r")
        infoBlock = f.read()
        f.close()
        print("----\n", len(infoBlock))
        create_qrcode(signatureAscii)
        generate_text_image(nomEtPrenom, institute)
        combine_image()
        combine_qrcode()

        timestampAscii = bin_to_base64("./ts/ts_respond.tsr")
        print("----\n", len(timestampAscii))
        messageStegano = infoBlock + timestampAscii
        img = Image.open("attestation.png")
        cacher(img, messageStegano)
        img.save("attestation.png")
        return "Create certificate successfully"
    return "Create certificate failed"