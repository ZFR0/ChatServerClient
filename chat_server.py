#!/usr/bin/env python3
"""Script Python per la realizzazione di un Server multithread
per connessioni CHAT asincrone.
Scheletro del programma ottenuto dal codice fornito 
nella settima esercitazione in laboratorio."""

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

""" La funzione che segue accetta le connessioni  dei client in entrata."""
def accetta_connessioni_in_entrata():
    while True:
        try:
            client, client_address = SERVER.accept()

            # ci serviamo di un dizionario per registrare i client
            addresses[client] = client_address
            
            #diamo inizio all'attività del Thread - uno per ciascun client
            Thread(target=client_handling, args=(client,client_address)).start()
            
            print("%s:%s si e' connesso al server. Login necessario per entrare in chat." % client_address)
            #al client che si connette per la prima volta fornisce alcune indicazioni di utilizzo
            client.send(bytes("Benvenuto, digita il tuo nome per cominciare.", "utf8"))
            
        except Exception as e:
            print("Non e' stato possibile accettare il client. Eccezione: %s" % e)

"""La funzione seguente gestisce la connessione di un singolo client."""
def client_handling(client,client_address):  # Prende il socket del client come argomento della funzione.
    try:
        acceptable_name=False
        while not acceptable_name:
            name = client.recv(BUFSIZ).decode("utf8")
            if name in clients.values():
                print("%s:%s ha provato ad unirsi con il nome %s, ma qualcuno con il nome %s è già presente in chat." % (client_address[0], client_address[1], name, name))
                client.send(bytes("Qualcuno con quel nome e' gia' presente in chat! Digita un'altro nome.", "utf8"))
            else: 
                if name == "{quit}":
                    print("%s:%s si e' disconnesso senza loggare." % client_address)
                    client.close()
                    break
                else:
                    acceptable_name=True
                    print("%s:%s si e' loggato con il nome %s e ora partecipa alla chat." % (client_address[0], client_address[1], name))
                    #da il benvenuto al client e gli indica come fare per uscire dalla chat quando ha terminato
                    welcome = 'Benvenuto %s! \n Per uscire dalla chat, chiudi la finestra o digita {quit} e premi invio.' % name
                    client.send(bytes(welcome, "utf8"))
                    msg = "%s si è unito alla chat!" % name
                    #messaggio in broadcast con cui vengono avvisati tutti i client connessi che l'utente x è entrato
                    broadcast(bytes(msg, "utf8"))
                    #aggiorna il dizionario clients creato all'inizio
                    clients[client] = name
                    client.send(bytes("Partecipanti attuali alla chat: %s" % list(clients.values()), "utf8"))
        
        #si mette in ascolto del thread del singolo client e ne gestisce l'invio dei messaggi o l'uscita dalla Chat
        while name != "{quit}":
            msg = client.recv(BUFSIZ)
            if msg != bytes("{quit}", "utf8"):
                broadcast(msg, name+": ")
            else:
                client.close()
                print("%s si e' disconnesso." % clients[client])
                del clients[client]
                broadcast(bytes("%s ha abbandonato la Chat." % name, "utf8"))
                break
    except ConnectionError:
        print("%s ha avuto un problema di connessione." % clients[client])
        broadcast(bytes("%s ha avuto un problema di connessione e non e' piu' qui." % name, "utf8"))
        client.close()
        del clients[client]
    except Exception as e:
        print("Errore nell'handling del client. Eccezione: %s" % e)

""" La funzione, che segue, invia un messaggio in broadcast a tutti i client."""
def broadcast(msg, prefisso=""):  # il prefisso è usato per l'identificazione del nome.
    for utente in clients:
        try:
            utente.send(bytes(prefisso, "utf8")+msg)
        except Exception as e:
            laddr = utente.getsockname()
            print("Non è stato possibile mandare il messaggio a %s:%s. Eccezione: %s" % (laddr[0], laddr[1], e))

        
clients = {}
addresses = {}

BUFSIZ = 1024
VALID = True

HOST = input('Inserire l\'indirizzo del server (premere invio senza scrivere nulla per localhost): ')
if not HOST:
    print("Inserito host nullo. localhost verrà usato automaticamente")
    HOST = 'localhost'

PORT = input('Inserire la porta del server host (premere invio senza scrivere nulla per 53000): ')
if not PORT:
    print("Inserita porta nulla. 53000 verrà usata automaticamente")
    PORT = 53000
else:
    PORT = int(PORT)
    

ADDR = (HOST, PORT)

try:  
    SERVER = socket(AF_INET, SOCK_STREAM)
    SERVER.bind(ADDR)
except Exception as e:
    SERVER.close()
    print("Impossibile effettuare il binding. Il socket e' probabilmente invalido. Eccezione: %s", e)
    print("Nuovo tentativo di binding con indirizzo e porta predefiniti")

    try: 
        HOST = 'localhost'
        PORT = 53000
        ADDR = (HOST, PORT)
        SERVER = socket(AF_INET, SOCK_STREAM)
        SERVER.bind(ADDR)
    except Exception as e:
        print("Tentativo fallito. Il server non può essere aperto. Eccezione: %s" % e)
        SERVER.close()
        VALID = False


if __name__ == "__main__" and VALID:
    try:    
        SERVER.listen(5)
        print("Il server si e' avviato con indirizzo %s e porta %s" % (HOST, PORT))
        print("La chat room e' online.")
        ACCEPT_THREAD = Thread(target=accetta_connessioni_in_entrata)
        ACCEPT_THREAD.start()
        ACCEPT_THREAD.join()
    except Exception as e:
        print("Qualcosa nel server e' andato storto. Eccezione: %s" % e)
    finally:
        SERVER.close()
