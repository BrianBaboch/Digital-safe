from OpenSSL import crypto
import os
import sys
import datetime
import requests
import time
from gen_certificate import url, read_binary_file, write_binary_file

def load_cert():
    available_certs = ""
    if(not os.path.exists("certs")):
            os.mkdir("certs")
    for root, dirs, files in os.walk(".\certs", topdown=False):
        for name in files:
            fileName = os.path.join(root, name)
            if(fileName.split(".")[-1] == "pem"):
                    available_certs += "," + fileName

    certNumb = (requests.post(url + "updateCert", data=available_certs).content).decode()
    if(certNumb == 0):
        return

    i = 0
    while (i < int(certNumb)):
        cert_buffer = requests.get(url + "loadCert").content
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_buffer)
        name = cert.get_subject().CN
        
        write_binary_file(".\\certs\\" + "_".join(name.split(" ")) + ".pem", 
            cert_buffer)
        i = i + 1

def crl_update():
    try:
        r = requests.get(url + "crlUpdate")
        write_binary_file("cert.crl", r.content)

        crl = crypto.load_crl(crypto.FILETYPE_ASN1, r.content)
        revoked_list = []
        
        for elt in crl.get_revoked():
            revoked_list.append(int(elt.get_serial().decode()))

        existing_cert = []
        for root, dirs, files in os.walk(".\certs", topdown=False):
            for name in files:
                fileName = os.path.join(root, name)
                if(fileName.split(".")[-1] == "pem"):
                        existing_cert.append(fileName)
        for elt in existing_cert:
            buffer = read_binary_file(elt)
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, buffer)
            if(cert.get_serial_number() in revoked_list):
                os.remove(elt)
        print("DONE")
    except:
        return
    
def main():
    crl_update()
    load_cert()

if __name__ == '__main__':  
    counter = 0
    error = True
    while (error):
        try:
            main()
            error = False
        except:
            if(counter >= 5):
                print("An error has occured please contact the server owner.")
            error = True
            counter += 1
            print("Failed to execute! Retrying again now.")
            time.sleep(5)