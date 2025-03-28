#!/usr/bin/env python3
"""Script relativa alla chat del client utilizzato per lanciare la GUI Tkinter.
Scheletro del programma ottenuto dal codice fornito 
nella settima esercitazione in laboratorio."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter as tkt

"""La funzione che segue ha il compito di gestire la ricezione dei messaggi."""
def receive():
    while True:
        try:
            #quando viene chiamata la funzione receive, si mette in ascolto dei messaggi che
            #arrivano sul socket
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            #visualizziamo l'elenco dei messaggi sullo schermo
            #e facciamo in modo che il cursore sia visibile al termine degli stessi
            msg_list.insert(tkt.END, msg)
            # Nel caso di errore e' probabile che il client abbia abbandonato la chat.
        except OSError as e:  
            print("Errore nella ricezione dati dal server. Forse il client ha abbandonato la chat o il server e' chiuso. Eccezione: %s " % e)
            close()
            break
        
"""La funzione che chiude il socket e la GUI della chat da parte del client."""     
def close():
    global is_socket_on
    if is_socket_on:
        is_socket_on=False
        try:
            client_socket.close()
        except OSError as e:
            print("Errore nella chiusura del socket. Eccezione: %s" % e)
        finestra.destroy()

"""La funzione che segue gestisce l'invio dei messaggi."""
def send(event=None):
    try:
        # gli eventi vengono passati dai binders.
        msg = my_msg.get()
        # libera la casella di input.
        my_msg.set("")
        # invia il messaggio sul socket
        client_socket.send(bytes(msg, "utf8"))
    except OSError:
        print("Errore nella trasmissione dati al server.")
        close()
        
    if msg == "{quit}":
        close()

"""La funzione che segue viene invocata quando viene chiusa la finestra della chat."""
def on_closing(event=None):
    my_msg.set("{quit}")
    send()

#----Connessione al Server----
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

BUFSIZ = 1024
ADDR = (HOST, PORT)

try:  
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(ADDR)
except Exception as e:
    print("Impossibile effettuare il binding. Il socket e' probabilmente invalido o il server e' chiuso. Eccezione: %s", e)
else:
    print("Connessione al server riuscita.")

    is_socket_on=True

    finestra = tkt.Tk()
    finestra.title("Chat")

    #creiamo il Frame per contenere i messaggi
    messages_frame = tkt.Frame(finestra)

    #creiamo una variabile di tipo stringa per i messaggi da inviare.
    my_msg = tkt.StringVar()
    #indichiamo all'utente dove deve scrivere i suoi messaggi
    my_msg.set("Scrivi qui i tuoi messaggi.")
    #creiamo una scrollbar per navigare tra i messaggi precedenti.
    scrollbar = tkt.Scrollbar(messages_frame)

    # La parte seguente contiene i messaggi.
    msg_list = tkt.Listbox(messages_frame, height=15, width=100, yscrollcommand=scrollbar.set)

    # Font e colori di background personalizzati
    msg_list.configure(bg='black', fg='white', font=('Courier New', 12))

    scrollbar.pack(side=tkt.RIGHT, fill=tkt.Y)
    msg_list.pack(side=tkt.LEFT, fill=tkt.BOTH)
    msg_list.pack()
    messages_frame.pack()

    #Creiamo il campo di input e lo associamo alla variabile stringa
    entry_field = tkt.Entry(finestra, textvariable=my_msg, width=50)
    # leghiamo la funzione send al tasto Return
    entry_field.bind("<Return>", send)

    entry_field.pack()
    #creiamo il tasto invio e lo associamo alla funzione send
    send_button = tkt.Button(finestra, text="Invio", command=send)
    #integriamo il tasto nel pacchetto
    send_button.pack()

    finestra.protocol("WM_DELETE_WINDOW", on_closing)

    receive_thread = Thread(target=receive)
    receive_thread.start()
    # Avvia l'esecuzione della Finestra Chat.
    tkt.mainloop()

