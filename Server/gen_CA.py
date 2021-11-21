from OpenSSL import crypto
import os
import sys
import datetime
import time
import random

ca_key_path = "ca.key"
ca_public_key_path = "ca.pubkey"
doc_path = "Docs/"
now = datetime.datetime.now()
expire = now + datetime.timedelta(days=3650)
current_date = now.strftime("%Y%m%d%H%M%SZ").encode()
expire_date = expire.strftime("%Y%m%d%H%M%SZ").encode()
TYPE_RSA = crypto.TYPE_RSA

def read_binary_file(path):
    f = open(doc_path + path, "r+b")
    content = f.read()
    f.close()
    return content

def write_binary_file(path, payload):
    f=open(doc_path + path, "w+b")
    f.write(payload)
    f.close()

def generatekey():
    if os.path.exists(doc_path + ca_key_path):
        print ("Key file exists: ")
        print (doc_path + ca_key_path)
        password = input("Enter key password: ")
        key = crypto.load_privatekey(crypto.FILETYPE_PEM, 
            read_binary_file(ca_key_path), password.encode())
        return(key)
    #Else write the key to the keyfile
    else:
        print("Generating Key Please standby")
        key = crypto.PKey()
        key.generate_key(TYPE_RSA, 2048)
        passphrase = input("Enter private key passphrase: ")
        private_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, key, 
            "aes256", passphrase.encode()) 
        public_key = crypto.dump_publickey(crypto.FILETYPE_PEM, key) 
        write_binary_file(ca_key_path, private_key)
        write_binary_file(ca_public_key_path, public_key)
    return(key)

def generateCaCert(pkey):
    ca_cert = crypto.X509()
    ca_cert.set_version(2)
    ca_cert.set_serial_number(random.randint(50000000,100000000))
    subj = crypto.X509Name(ca_cert.get_subject())

    subj.__setattr__("C", input("Enter country name: "))
    subj.__setattr__("ST", input("Enter state name: "))
    subj.__setattr__("L", input("Enter city name: "))
    subj.__setattr__("O", input("Enter organization name: "))
    subj.__setattr__("OU", input("Enter organization unit name: "))
    subj.__setattr__("CN", input("Enter common name: "))
    subj.__setattr__("emailAddress", input("Enter email address: "))

    ca_cert.set_subject(subj)
    ca_cert.gmtime_adj_notBefore(0)
    ca_cert.gmtime_adj_notAfter(10*365*24*60*60)

    ca_cert.set_issuer(subj)
    ca_cert.set_pubkey(pkey)

    #add ca extension to certificate
    ca_cert.add_extensions([crypto.X509Extension("basicConstraints"
        .encode(), True, "CA:TRUE, pathlen:0".encode())])
    ca_cert.add_extensions([crypto.X509Extension("subjectKeyIdentifier"
        .encode(), False, "hash".encode(), subject=ca_cert)])
    ca_cert.add_extensions([crypto.X509Extension("authorityKeyIdentifier"
        .encode(), False, "keyid,issuer:always".encode(), issuer=ca_cert)])
    ca_cert.add_extensions([crypto.X509Extension("keyUsage"
        .encode(), True, "keyCertSign, cRLSign".encode())])

    ca_cert.sign(pkey, "sha256")
    ca_cert_buffer = crypto.dump_certificate(crypto.FILETYPE_PEM, ca_cert)
    write_binary_file("ca.pem", ca_cert_buffer)
    return (ca_cert_buffer)

def create_folder ():
    if not os.path.exists("Docs"):
        os.makedirs("Docs")

def main():
    create_folder()
    myKey = generatekey()
    generateCaCert(myKey)

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