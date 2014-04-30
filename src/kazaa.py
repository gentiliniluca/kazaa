import GestionePeer
import GestioneSuperpeer
import Server 
import Util
import os
import signal
import SearchResultService
import Connessione

class Kazaa:
    
    print("Avvio kazaa")
    while True:
        print ("Si vuole avviare il programma in:")
        print("\t 1. Modalita PEER")
        print("\t 2. Modalita SUPER-PEER")
        out=raw_input("\nOperazione scelta: ")
        if(int(out) >= 1 and int(out) <= 2):
                break
        print("Valore inserito errato! (valore compreso tra 1 e 2)")
        
    
    if(int(out)==1):
        Util.USEMODE="PEER"
        try:
            conn_db=Connessione.Connessione()
            SearchResultService.SearchResultService.delete(conn_db.crea_cursore())
        finally:
            conn_db.esegui_commit()
            conn_db.chiudi_connessione()
        GestionePeer.GestionePeer.PeerManagement()
    else:
        Util.USEMODE="SUPERPEER"
        GestioneSuperpeer.GestioneSuperpeer.SuperpeerManagement()
        


#    pid = os.fork()
#    if(pid == 0): #figlio per gestire operazioni menu
#        operazione_utente = 1
#        while(int(operazione_utente) != 0):
#            operazione_utente = Client.Client.visualizza_menu_principale()
#            print("Valore: " + operazione_utente)
#            
#            #ricerca file
#            if(int(operazione_utente) == 1):            
#                Client.Client.searchHandler()
#            
#            #ricerca vicini
#            if(int(operazione_utente) == 2):            
#                Client.Client.nearHandler() 
#                
#            #aggiunta file
#            if(int(operazione_utente) == 3):            
#                Client.Client.addFile()
#            
#            #download file
#            if(int(operazione_utente) == 4):
#                Client.Client.downloadHandler()
#                       
#                     
#        print("Fine operazioni utente")
#        #pulisco DB quando esco
#        os.kill(os.getppid(), signal.SIGKILL)
#        
#        
#    else: #gestisco funzionalita server 
#        s = Server.Server.initServerSocket()
#        while 1:
#            print("\t\t\t\t\t\t\t\t\tAttesa richiesta peer")
#            client, address = s.accept()
#            newpid = os.fork()
#            if(newpid == 0):
#                try:
#                    s.close()
#                                        
#                    #pulizia pkt vecchi da 300 s        
#                    Server.Server.expiredPacketHandler()
#                                    
#                    receivedString = Server.Server.readSocket(client)
#                    operazione = receivedString[0:4]
#                    
#                    if operazione == "":
#                        break
#                                                            
#                    #operazione NEAR
#                    if operazione.upper() == "NEAR":
#                        Server.Server.nearHandler(receivedString)                    
#        
#                    #operazione ANEA
#                    if operazione.upper() == "ANEA":
#                        Server.Server.addNewNear(receivedString)
#                        
#                    #operazione QUER
#                    if operazione.upper()=="QUER":
#                        Server.Server.searchHandler(receivedString)
#                    
#                    #operazione AQUE
#                    if operazione.upper()=="AQUE":
#                        Server.Server.searchResultHandler(receivedString)
#                        
#                    #operazione RETR
#                    if operazione.upper() == "RETR":
#                        Server.Server.uploadHandler(client, receivedString)
#
#                except Exception as e: 
#                    print e
#                    print("\t\t\t\t\t\t\t\t\tErrore ricezione lato server")
#                    
#                finally:
#                    client.close() 
#                    stringa_ricevuta_server = ""
#                    os._exit(0) 
#                
#            else:
#                client.close()
#    
#        print("Terminato parte server")
#    
    