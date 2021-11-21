from OpenSSL import crypto
import os
import sys
import datetime
import random
import manage_db
import json

now = datetime.datetime.now()
expire = now + datetime.timedelta(days=3650)
current_date = now.strftime("%Y%m%d%H%M%SZ").encode()
expire_date = expire.strftime("%Y%m%d%H%M%SZ").encode()

doc_path = "Docs/"
cert_path = "cert.pem"
ca_cert_path = "ca.pem"
ca_key = "ca.key"
ca_pass = ""
loaded_cert = []

def read_binary_file(path):
    f = open(doc_path + path, "r+b")
    content = f.read()
    f.close()
    return content

def write_binary_file(path, payload):
    f=open(doc_path + path, "w+b")
    f.write(payload)
    f.close()

ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, 
    read_binary_file(ca_cert_path))
ca_cert_buffer = crypto.dump_certificate(crypto.FILETYPE_PEM, ca_cert)
ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, read_binary_file(ca_key))

def signCert(req):
    req = crypto.load_certificate_request(crypto.FILETYPE_PEM, req)
    cert = crypto.X509()
    cert.set_version(2)
    cert.set_serial_number(random.randint(50000000,100000000))
    cert.set_subject(req.get_subject())

    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10*365*24*60*60)
    
    cert.set_issuer(ca_cert.get_subject())
    cert.set_pubkey(req.get_pubkey())

    #extensions
    cert.add_extensions([crypto.X509Extension("subjectKeyIdentifier".encode(), False, "hash".encode(), cert, ca_cert)])

    cert.add_extensions([crypto.X509Extension("authorityKeyIdentifier"
        .encode(), False, "keyid,issuer:always".encode(), cert, ca_cert)])

    cert.add_extensions([crypto.X509Extension("issuerAltName"
        .encode(), False, "issuer:copy".encode(), cert, ca_cert)])

    #cert.add_extensions([crypto.X509Extension("subjectAltName"
    #    .encode(), True, "email:copy".encode(), cert, ca_cert)])
        
    cert.add_extensions([crypto.X509Extension("basicConstraints"
        .encode(), True, "CA:FALSE".encode(), cert, ca_cert)])

    cert.add_extensions([crypto.X509Extension("keyUsage"
        .encode(), True, "digitalSignature, keyEncipherment".encode(), cert, ca_cert)])

    cert.sign(ca_key, "sha256")
    cert_pem = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
    common_name = (req.get_subject()).get_components()[5][1].decode()
    if(not os.path.exists(doc_path + "certs")):
        os.mkdir(doc_path + "certs")
    write_binary_file("certs/" + "_".join(common_name.split(" ")) + ".pem", cert_pem)
    return (cert_pem)

def verify_identity(obj_id, key_id, signed_id):
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, 
        read_binary_file("certs/" + obj_id + ".pem"))
    print("certs/" + obj_id + ".pem")
    try:
        crypto.verify(cert, signed_id, key_id, "sha256")
    except:
        print("Wrong Signature")
        return

def info_func(con, obj_id, signed_id):
    try:
        if not check_obj_status(con, obj_id):
            return("00")
        verify_identity(obj_id, obj_id, signed_id)
        result = manage_db.sql_select_obj_key(con, obj_id)
        d={}
        i=0
        print(result)
        return(json.dumps(result))

    except:
        return("Error wrong signature")

def access_func(con, obj, key, signed_key,):
    try:
        if not check_obj_status(con, obj):
            return("00")
        verify_identity(obj, key, signed_key)
        result = manage_db.sql_select_key(con, key)
        start_date = datetime.datetime.strptime(result[0][3], '%d/%m/%Y')
        end_date = result[0][4]
        end_date_format = ""
        if(end_date != ""):
            end_date_format = datetime.datetime.strptime(result[0][4], '%d/%m/%Y')
            print("End date != than 0")
        current_date = datetime.datetime.today()
        resource = result[0][1]
        if(current_date < start_date):
            return("0")
        elif(end_date != ""):
            if(current_date > end_date_format):
                return("1")
            else:
                return(resource)
        else:
            return(resource)
    except:
        return("Error wrong signature")

def check_obj_status(con, obj):
    tmp = manage_db.sql_select_object(con, obj)
    res = int(tmp[0][1])
    return(res)