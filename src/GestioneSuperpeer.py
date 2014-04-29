import Client 
import Connessione
import Server
import PeerService 
import Util
import os
import signal

class GestioneSuperpeer:
    
    @staticmethod
    def SuperpeerManagement():
        print("\nAvvio come SuperPeer")
        
        pid = os.fork()
        if(pid == 0): #figlio per gestire operazioni menu
            operazione_utente = 1
            
            SessionID = Client.Client.loginSuperpeer()
            
            while(int(operazione_utente) != 0):
                operazione_utente = Client.Client.visualizza_menu_principale()           
                           
                #ricerca file
                if(int(operazione_utente) == 1):            
                    Client.Client.searchHandler(SessionID)
                                        
                #aggiunta file
                if(int(operazione_utente) == 2):            
                    Client.Client.addFile(SessionID)
                
                #rimuovi file
                if(int(operazione_utente) == 3):            
                    Client.Client.deleteFile(SessionID)
                    
                #download file
                if(int(operazione_utente) == 4):            
                    Client.Client.downloadFile()        
                    
                #ricerca vicini
                if(int(operazione_utente) == 5):            
                    Client.Client.superNearSearchHandler()
       
            print("Fine operazioni utente")
            #logout all'uscita
            Client.Client.logout(SessionID)
            os.kill(os.getppid(), signal.SIGKILL)
                
        else: #gestisco funzionalita server 
            s = Server.Server.initServerSocket()
            print("\n\t\t\t\t\t\tPronto a ricevere richieste...")
            while 1:            
                clientSocket, address = s.accept()
                print("\n\t\t\t\t\t\tConnesso al peer con indirizzo: " + str(address))
                newpid = os.fork()
                if(newpid == 0):
                    try:
                        s.close()

                        #Server.Server.expiredPacketHandler()

                        receivedString = Server.Server.readSocket(clientSocket)
                        operazione = receivedString[0:4]

                        if operazione == "":
                            break
                        
                        #ricerca supernodi vicini
                        if operazione.upper() == "SUPE":
                            Server.Server.superNearSearchHandler(receivedString, clientSocket)
                            
                        #raccolta risultati ricerca supernodi vicini
                        if operazione.upper() == "ASUP":
                            Server.Server.superNearSearchResultHandler(receivedString)

                        #login
                        if operazione.upper() == "LOGI":
                            Server.Server.loginHandler(receivedString, clientSocket)

                        #logout         
                        if operazione.upper() == "LOGO":
                            Server.Server.logoutHandler(receivedString, clientSocket)                   

                        #aggiunta file
                        if operazione.upper() == "ADFF":
                            Server.Server.addFileHandler(receivedString)

                        #rimozione file
                        if operazione.upper() == "DEFF":
                            Server.Server.deleteFileHandler(receivedString)  

                        #ricerca file per conto di un altro supernodo
                        if operazione.upper() == "QUER":
                            Server.Server.fileSearchHandler(receivedString)

                        #raccolta risultati della ricerca di un file
                        if operazione.upper() == "AQUE":
                            Server.Server.fileSearchResultHandler(receivedString)   

                        #ricerca file per conto di un peer del mio cluster
                        if operazione.upper() == "FIND":
                            Server.Server.fileSearchRequestHandler(receivedString, clientSocket) 
                            
                        #operazione RETR
                        if operazione.upper() == "RETR":
                            Client.Client.uploadHandler(clientSocket,receivedString)

                    except Exception as e: 
                        print e
                        print("Errore ricezione lato server")

                    finally:
                        clientSocket.close() 
                        stringa_ricevuta_server = ""
                        os._exit(0) 

                else:
                    clientSocket.close()

        print("Terminato.")