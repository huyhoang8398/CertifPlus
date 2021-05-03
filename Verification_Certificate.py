import base64
from PIL import Image
from Creation_Stegano import recuperer
import subprocess
import zbarlight


def get_qrcode_png():
    attestation = Image.open("attestation_a_verifier.png")
    qr_image = attestation.crop((1418, 934, 1418 + 210, 934 + 210))
    qr_image.save("qrCrop.png", "PNG")
    print("Get QRCode from attestation")


def get_data_from_qrcode():
    image = Image.open("qrCrop.png")
    data = zbarlight.scan_codes(['qrcode'], image)
    data = base64_to_bin(data[0])
    print(data)
    f = open("verify_sig_qrcode.sig", "wb")
    f.write(data)
    f.close()


def base64_to_bin(data):
    return base64.b64decode(data)


def verify_timestamp(data):
    ProcessTSQ = subprocess.Popen([
        "openssl ts -query -data ./verify_sig_qrcode.sig -no_nonce -sha512 -cert -out ./ts/ts_query_verify.tsq"
    ],
                                  shell=True,
                                  stdout=subprocess.PIPE)

    (output, error) = ProcessTSQ.communicate()
    if ProcessTSQ.returncode == 0:
        print("Create timestamp-query")
    else:
        print("Create timestamp-query failed")

    ProcessTSR = subprocess.Popen([
        "openssl ts -verify -in {} -queryfile ./ts/ts_query_verify.tsq -CAfile ./ts/cacert.pem -untrusted ./ts/tsa.crt"
        .format(data)
    ],
                                  shell=True,
                                  stdout=subprocess.PIPE)
    (output, error) = ProcessTSR.communicate()

    if ProcessTSR.returncode == 0 and output.decode() == 'Verification: OK\n':
        print("Verify success timestamp")
        return True
    else:
        return False


def verify_signature(data):
    Process = subprocess.Popen([
        "openssl dgst -verify CA/ecc.ca.pubkey.pem -signature {} info.txt".
        format(data)
    ],
                               shell=True,
                               stdout=subprocess.PIPE)

    (output, error) = Process.communicate()
    if Process.returncode == 0 and output.decode() == 'Verified OK\n':
        print("verify success signature")
        return True
    else:
        return False


def get_data_from_stegano():
    image = Image.open("attestation_a_verifier.png")
    fullMessage = recuperer(image, 7388)
    # print(fullMessage)
    infoBlock = fullMessage[:64]
    timeStamp = fullMessage[64:]

    print(len(infoBlock))
    print(len(timeStamp))
    timeStamp = base64_to_bin(timeStamp)
    print(len(timeStamp))

    f = open("verify_timestamp.tsr", "wb")
    f.write(timeStamp)
    f.close()

    f = open("info.txt", "w")
    f.write(infoBlock)
    f.close()

    return infoBlock, timeStamp


def verify_certificate():
    get_qrcode_png()
    get_data_from_qrcode()
    _, _ = get_data_from_stegano()
    if (verify_signature("verify_sig_qrcode.sig")
            == True) and (verify_timestamp("verify_timestamp.tsr") == True):
        return "Verify certificate successfully"
