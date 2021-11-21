import manage_db
import datetime

def banner():
    print("\n*****************************************")
    print("* SR2I PRIM - Insert Data Into Server   *")
    print("*****************************************")

def menu():
    print("------------------")
    print("Choississer une des fonctions suivantes :")
    print("------------------")
    print("1- Ajouter un objet avec son status.")
    print("2- Ajouter une ressource et l'associer à un objet.")
    print("3- Sortir de l'application.")
    print("------------------")

def main():
    banner()
    menu()
    con = manage_db.sql_connection()
    while True:
        try:
            choice = int(input("\nVotre Choix : "))
        except:
            print("\nVotre choix est invalide")
            menu()
        if choice == 1:
            obj=[]
            try:
                tmp = str(input("Entrer l'identifiant de l'objet: "))
                obj.append(tmp)
                tmp = int(input("Entrer le statut de l'objet: "))
                obj.append(tmp)
                manage_db.sql_insert(con, obj, "objects")
            except:
                print("Wrong format for inputs!!")
        elif choice == 2:
            obj=[]
            try:
                tmp = str(input("\nEntrer l'identifiant de la ressource: "))
                obj.append(tmp)
                tmp = str(input("\nEntrer le lien vers la ressouce: "))
                obj.append(tmp)
                tmp = str(input("\nEntrer une description de la ressource: "))
                obj.append(tmp)
                tmp = str(input("\nEntrer l'identifiant de l'objet associé: "))
                obj.append(tmp)
                tmp = str(input("\nEntrer la date de début de validité: "))
                obj.append(tmp)
                tmp = str(input("\nEntrer la date de fin de validité: "))
                obj.append(tmp)
                manage_db.sql_insert(con, obj, "safe_keys")
            except:
                print("Wrong format for inputs!!")
        elif choice == 3:
            print("\nArret du programme!!\n")
            exit()
        else:
            print("\n\nVotre choix est invalide")
            menu()
           
if __name__ == '__main__':
    main()

