import Client 
import Server 
import Util
import os
import signal

class GestionePeer:
    
    @staticmethod
    def PeerManagement():
        print("\nAvvio come peer")
        
        pid = os.fork()
        if(pid == 0): #figlio per gestire operazioni menu
            operazione_utente = 1
            SessionID=" "
            while(int(operazione_utente) != 0):
                operazione_utente = Client.Client.visualizza_menu_principale()
                #print("Valore: " + str(operazione_utente) +" per il sessionID= "+SessionID)
                           
                #ricerca file
                if(int(operazione_utente) == 1):            
                    Client.Client.searchHandler(SessionID)
                    
                #login
                if(int(operazione_utente) == 2):            
                    SessionID=Client.Client.login(SessionID)
                
                #carica file
                if(int(operazione_utente) == 3):            
                    Client.Client.addFile(SessionID)
                    
                #download file
                if(int(operazione_utente) == 4):            
                    Client.Client.downloadFile()
                    
                #rimuovi file
                if(int(operazione_utente) == 5):            
                    Client.Client.deleteFile(SessionID)
                    
                #logout
                if(int(operazione_utente) == 6):            
                    SessionID=Client.Client.logout(SessionID)
       
            print("Fine operazioni utente")
            #pulisco DB quando esco
            os.kill(os.getppid(), signal.SIGKILL)
        
        
        else: #gestisco funzionalita server 
            s = Client.Client.initServerSocket()
            while 1:
                print("\t\t\t\t\t\t\t\t\tAttesa richiesta peer")
                client, address = s.accept()
                newpid = os.fork()
                if(newpid == 0):
                    try:
                        s.close()

                        receivedString = Client.Client.readSocket(client)
                        operazione = receivedString[0:4]

                        if operazione == "":
                            break

                        #operazione RETR
                        if operazione.upper() == "RETR":
                            Client.Client.uploadHandler(client,receivedString) 
                            
                        #operazione SUPE  serve??
                        if operazione.upper() == "SUPE":
                            Client.Client.uploadHandler(client,receivedString)

                        

                    except Exception as e: 
                        print e
                        print("\t\t\t\t\t\t\t\t\tErrore ricezione lato server")

                    finally:
                        client.close() 
                        stringa_ricevuta_server = ""
                        os._exit(0) 

                else:
                    client.close()

            print("Terminato parte server del peer")
    
