import base64
from PIL import Image
from Creation_Stegano import recuperer
import subprocess
import zbarlight


def get_qrcode_png():
    attestation = Image.open("attestation.png")
    qr_image = attestation.crop((1418, 934, 1418 + 210, 934 + 210))
    qr_image.save("qrCrop.png", "PNG")
    print("Get QRCode from attestation")


def get_data_from_qrcode():
    image = Image.open("qrCrop.png")
    data = zbarlight.scan_codes(['qrcode'], image)
    data = base64_to_bin(data[0])
    print(data)
    f = open("verify_sig.txt", "wb")
    f.write(data)
    f.close()

def base64_to_bin(data):
    return base64.b64decode(data)


def verify_timestamp():
    Process = subprocess.Popen([
        "openssl ts -verify -in file.tsr -queryfile file.tsq -CAfile cacert.pem -untrusted tsa.crt"
    ],
                    shell=True,
                    stdout=subprocess.PIPE)

    (result, ignorer) = Process.communicate()
    if Process.returncode == 0:
        print("create signature")
        return True
    else:
        return False


def verify_signature(data):
    Process = subprocess.Popen([
        "openssl dgst -verify ./CA/ecc.ca.pubkey.pem -signature {} ./CA/info.txt"
        .format(data)
    ],
                               shell=True,
                               stdout=subprocess.PIPE)

    (result, ignorer) = Process.communicate()
    if Process.returncode == 0 and result.decode() == 'Verified OK\n':
        print("verify success")
        print(result)
        return True
    else:
        return False


get_qrcode_png()
get_data_from_qrcode()
verify_signature("verify_sig.txt")