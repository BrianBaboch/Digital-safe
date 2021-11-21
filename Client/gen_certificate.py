from OpenSSL import crypto
import os
import sys
import datetime
import time
import requests
import base64
import json

doc_path = "Docs/"
common_name = ""
key_passphrase = ""
privatekeypath = ""
publickeypath = "publicKey.pubkey"
reqpath = ""
csrpath = "req.csr"
crtpath = "certificate.crt"
key = crypto.PKey()
TYPE_RSA = crypto.TYPE_RSA
TYPE_DSA = crypto.TYPE_DSA

now = datetime.datetime.now()
d = now.date()

url = "http://localhost:5000/"

def banner():
    print("\n*****************************************")
    print("* SR2I PRIM - Application Mobile        *")
    print("*****************************************")

def menu():
    print("------------------")
    print("Choississer une des fonctions suivantes :")
    print("------------------")
    print("1- Générer une paire de clé et demander un certificat.")
    print("2- Importer un certificat s'il est déja créé.")
    print("3- Demander les informations relatives a vos ressources.")
    print("4- Accéder a une ressource.")
    print("5- Révoquer votrer objet.")
    print("6- Sortir de l'application.")
    print("------------------")

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
    global privatekeypath
    global publickeypath
    global common_name
    global key_passphrase
    common_name = input("Enter object ID: ")
    privatekeypath = "_".join(common_name.split(" ")) + ".key"
    publickeypath = "_".join(common_name.split(" ")) + ".pubkey"
    
    if (os.path.exists(doc_path + privatekeypath)):
        print ("Key file exists: ")
        print (doc_path + privatekeypath)
        key_passphrase = input("Enter key password: ")
        myKey = crypto.load_privatekey(crypto.FILETYPE_PEM, 
            read_binary_file(privatekeypath), key_passphrase.encode())
        return(myKey)
    #Else write the key to the keyfile
    else:
        print("Generating Key Please standby")
        key.generate_key(TYPE_RSA, 2048)
        tmp_passphrase = input("Enter private key passphrase: ")
        key_passphrase = tmp_passphrase
        private_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, key, 
            "aes256", key_passphrase.encode()) 
        public_key = crypto.dump_publickey(crypto.FILETYPE_PEM, key) 
        write_binary_file(privatekeypath, private_key)
        write_binary_file(publickeypath, public_key)
    return(key)

def createCertRequest(pkey):
    #email = input("Enter your email address: ")

    req = crypto.X509Req()
    req.get_subject().C = "FR"
    req.get_subject().ST = "75"
    req.get_subject().L = "Paris"
    req.get_subject().O = "Telecom-Paris"
    req.get_subject().OU = "SR2I-PRIM"
    req.get_subject().CN = common_name
    #req.get_subject().emailAddress = email
    req.set_pubkey(pkey)
    req.sign(pkey, "sha256")
    reqBinary = crypto.dump_certificate_request(crypto.FILETYPE_PEM, req)
    global reqpath
    reqpath = "_".join(common_name.split(" ")) + ".req"
    write_binary_file(reqpath, reqBinary)

def main():
    banner()
    menu()
    while True:
        try:
            choice = int(input("\nVotre Choix : "))
        except:
            print("\nVotre choix est invalide")
            menu()
        if choice == 1:
            create_folder()
            pkey = generatekey()
            createCertRequest(pkey)
            req_pem = read_binary_file(reqpath)
            '''
            ca_cert = requests.get(url + "ca")
            write_binary_file("ca.pem", ca_cert.content)
            '''
            r = requests.post(url + "data", data = req_pem)
            cert_path = "_".join(common_name.split(" ")) + ".pem"
            write_binary_file(cert_path, r.content)
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, 
                read_binary_file(cert_path))
            private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, 
                read_binary_file(privatekeypath), key_passphrase.encode())
            p12 = crypto.PKCS12()
            p12.set_privatekey(private_key)
            p12.set_certificate(cert)
            write_binary_file("_".join(common_name.split(" ")) + ".p12", 
            p12.export((input("Enter a passphrase for the PKCS12 certificate: "))
                .encode()))
            print("Certificat créé.\n")
            menu()
        elif choice == 2:
            pkey = generatekey()
        elif choice == 3:
            request_info()
        elif choice == 4:
            try:
                res = str(input("Choisissez la ressource vous souhaitez avoir : "))
            except:
                print("Votre choix est invalide")
            request_access(res)
        elif choice == 5:
            revoke()
        elif choice == 6:
            exit()
        else:
            print("\n\nVotre choix est invalide")
            menu()

def create_folder ():
    if not os.path.exists("Docs"):
        os.makedirs("Docs")

def request_info():
    obj_name, sig = get_signature()
    payload = str(obj_name + "*" + base64.b64encode(sig).decode('utf-8'))
    r = requests.post(url + "info", data = payload)
    if(str(r.content.decode()) == "00"):
        print("The object you're using is revoked.")
        return
    result = json.loads(r.content)
    i = 1
    print("You have access to the following keys:\n")
    for k in result:
        print("Key " + str(i) + ": " + str(k[0]))
        print("Accessible on: " + str(k[2]))
        print("Valid until: " + str(k[3]))
        print("\n")
        i+=1

def request_access(key):
    obj_name, res_id, sig = get_signature(key)
    payload = str(obj_name + "*" + res_id + "*" + base64.b64encode(sig).decode('utf-8'))
    r = requests.post(url + "access", data = payload)
    result = r.content.decode()
    if(str(result) == "00"):
        print("The object you're using is revoked.")
        return
    elif(str(result) == "0"):
        print("You're not allowed to access the resource yet.")
    elif(str(result) == "1"):
        print("The resource has expired and cannot be accessed anymore.")
    else:
        print("This is the ressource you asked for: " + str(result))

def get_signature(tmp=""):
    key_name = ""
    obj_name = ""
    payload = ""
    for file in os.listdir("./Docs"):
        if(file.endswith(".key")):
            key_name = file
            obj_name = file.split(".")[0]
            break
    if(key_name == ""):
        print("Missing private key")
        return
    if(tmp == ""):
        payload = obj_name
    else:
        print("Payload available")
        payload = tmp
    sig = crypto.sign(crypto.load_privatekey(crypto.FILETYPE_PEM, 
        read_binary_file(key_name), key_passphrase.encode()), payload.encode(), "sha256")
    if(tmp == ""):
        return(obj_name, sig)
    else:
        return(obj_name, payload, sig)

def revoke():
    obj_name, sig = get_signature()
    r = requests.post(url + "revoke", data = obj_name)
    result = r.content.decode()
    print(str(result))

if __name__ == '__main__':  
    counter = 0
    error = True
    try:
        main()
    except:
        print("\nArret du programme!!")
    '''
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
    '''