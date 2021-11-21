from flask import Flask, jsonify, request
from CA_functions import signCert, ca_cert_buffer, info_func, access_func
import manage_db
import base64

app = Flask (__name__)

#signs and returns the certificate to the client
@app.route('/data', methods = ['GET', 'POST'])
def sign_cert():
    if (request.method == 'POST'):
        req = request.data.decode()
        cert = signCert(req)
        return(cert)

#returns the ca certificat
@app.route('/ca', methods = ['GET', 'POST'])
def get_ca_cert():
    if (request.method == 'GET'):
        return(ca_cert_buffer)

#revokes the client's certificat
@app.route('/revoke', methods = ['GET', 'POST'])
def revoke_cert():
    if (request.method == 'POST'):
        obj = request.data.decode()
        manage_db.deactivate_object(con, obj)
        #return(revoke(request.data))
        return(obj + " was deactivated")

#ask for information related to keys I have access to
@app.route('/info', methods = ['GET', 'POST'])
def info():
    #request should contain the object Id and the object id signed by the private key
    if (request.method == 'POST'):        
        res = (request.data.decode()).split("*")
        obj = res[0]
        sig = base64.b64decode(res[1])
        return(info_func(con, obj, sig))

#ask for access to the resource
@app.route('/access', methods = ['GET', 'POST'])
def access_data():
    #request should contain the ressource Id and the ressource id signed by the private key
    if (request.method == 'POST'):
        res = (request.data.decode()).split("*")
        obj = res[0]
        print("Obj is: " + obj)
        key = res[1]
        print("key is: " + key)
        sig = base64.b64decode(res[2])
        return(access_func(con, obj, key, sig))

if __name__ == '__main__':
    try:
        con = manage_db.sql_connection()
        cur = con.cursor()
        print("Conx established to DB")
        app.run(host='localhost', port=5000)
        con.close()
        print("Connection closed")
    except:
        print("Error")
        con.close()
