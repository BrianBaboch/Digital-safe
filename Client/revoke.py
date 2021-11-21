from OpenSSL import crypto
import os
import sys
import datetime
import requests
import time
from gen_certificate import url, read_binary_file, write_binary_file

def revoke(cert_path):
    if (not os.path.exists(cert_path)):
        print("Certificate doesn't exsit")
        return
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, 
        read_binary_file(cert_path))
    serial_number = cert.get_serial_number()
    myData = str(serial_number) + "," + cert_path
    try:
        r = requests.post(url + "revoke", data = myData)
        write_binary_file("cert.crl", r.content)
        os.remove(cert_path)
    except:
        pass

def main():
    #check if the name was given with the extension or not
    cert = input("enter the name of your certificate: ")
    if(len(cert.split(".")) == 1):
        revoke(cert + ".pem")
    else:
        revoke(cert)

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