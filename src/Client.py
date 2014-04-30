import Connessione
import random
import socket
import string
import Util
import PeerService
import SharedFile
import SharedFileService
import SearchResult
import SearchResultService
import sys
import os
import PacketService
import SuperNearService


from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL)

class Client:
    
    global SIZE
    SIZE = 1024
    
    @staticmethod
    def visualizza_menu_principale():
        
        while True:
            if(Util.USEMODE=="PEER"):
                print("\n************************\n*  1 - Ricerca File    *\n*  2 - Login           *\n*  3 - Carica File     *\n*  4 - Download File   *\n*  5 - Rimuovi File    *\n*  6 - Logout          *\n*  0 - Fine            *\n************************")
            else:
                print("\n************************\n*  1 - Ricerca File    *\n*  2 - Carica File     *\n*  3 - Rimuovi File    *\n*  4 - Download File   *\n*  5 - Ricerca Vicini  *\n*  0 - Fine            *\n************************")
            out=raw_input("\nOperazione scelta: ")
            if(Util.USEMODE=="PEER" and (int(out) >= 0 and int(out) <= 6 ) or Util.USEMODE=="SUPERPEER" and(int(out) >= 0 and int(out) <= 5) ):
                break
            print("Valore inserito errato!")
        
        return out
    
    
    @staticmethod
    def login(SessionID):
        stringa_da_trasmettere="LOGI"+Util.HOST+Util.Util.adattaStringa(5,str(Util.PORT) )
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.connect((Util.IPSuperPeer, int(Util.PORTSuperPeer) ))
            sock.send(stringa_da_trasmettere.encode())
            risposta=sock.recv(20)
            print("Session id:"+risposta[4:20])
            nuovosessionid=risposta[4:20]
            sock.close()
        except Exception as e:
            print e
            print "Errore login"
        if(nuovosessionid=="0000000000000000"):
            return SessionID
        else:
            return nuovosessionid
            
    @staticmethod
    def logout(SessionID):
       
        if(SessionID != "" and SessionID != "0000000000000000"):
            stringa_da_trasmettere="LOGO"+SessionID
            
            try:
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                sock.connect((Util.IPSuperPeer, int(Util.PORTSuperPeer) ))
                sock.send(stringa_da_trasmettere.encode())
                risposta=sock.recv(7)
                print("Session id:"+SessionID)
                print "File eliminati dal superpeer: "+str(risposta[4:7])
                sock.close()
                #quando faccio il logout elimino tutti i record dalla tabella sharedfile
                conn_db=Connessione.Connessione()
                SharedFileService.SharedFileService.delete(conn_db.crea_cursore())
                conn_db.esegui_commit()
                conn_db.chiudi_connessione()
            except Exception as e:
                print e
                print "Errore logout"
        return ""
    
    
    @staticmethod
    def addFile(SessionID):
        nomefile=""
        filemd5=""
        
        #aggiungo file nella tabella del peer SharedFile
        try:
            conn_db = Connessione.Connessione()
            nomefile = raw_input("Inserire il nome del file: " + Util.LOCAL_PATH)
            filemd5 = Util.Util.get_md5(Util.LOCAL_PATH + nomefile)
            #print("md5: " + filemd5+"lunghezza: "+str(len(filemd5))+ "nome: " + nomefile)
            file = SharedFileService.SharedFileService.insertNewSharedFile(conn_db.crea_cursore(), filemd5, nomefile)
            
        except Exception as e:
            print e
            print("Errore aggiunta file")
        
        finally:
            conn_db.esegui_commit()
            conn_db.chiudi_connessione()
        
        #formatto e invio stringa di aggiunta file nel superpeer    
        try:
            nomefile = Util.Util.aggiungi_spazi_finali(nomefile,100)
            stringa_da_inviare="ADFF"+SessionID+filemd5+nomefile
            #print(stringa_da_inviare)
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.connect((Util.IPSuperPeer, int(Util.PORTSuperPeer) ))
            sock.send(stringa_da_inviare)
            sock.close()
        except Exception as e:
            print e
            print("Errore per contattare il superpeer in add file")
        
    @staticmethod
    def deleteFile(SessionID):
        
        ricerca=""
        sharedfile=[]
        choice=0
        try:
            ricerca=raw_input("Inserire stringa di ricerca del file: ")
            conn_db = Connessione.Connessione()
            sharedfile=SharedFileService.SharedFileService.getSharedFiles(conn_db.crea_cursore(),ricerca)
            i = 0
            while i < len(sharedfile):
                print("\t"+str(i + 1) + ".\t" + sharedfile[i].filename)
                i = i + 1
        
            #il valore di choice e' incrementato di uno
            choice = int(raw_input("\t  Scegliere il numero del file da cancellare (0 annulla): ")) 
            if(choice>0):
                sharedfile[choice-1].delete(conn_db.crea_cursore())
                print("File eliminato")
            
        except Exception as e:
            print e
            print"Errore nell'eliminazione del file da database locale"
        
        finally:
            conn_db.esegui_commit()
            conn_db.chiudi_connessione()
            
        try:
            if(choice>0):
                stringa_da_inviare="DEFF"+SessionID+sharedfile[choice-1].filemd5
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                sock.connect((Util.IPSuperPeer, int(Util.PORTSuperPeer) ))
                sock.send(stringa_da_inviare)
                sock.close()
            
        except Exception as e:
            print e
            print"Errore nel contattare il superpeer nell'eliminazione del file"
            
    @staticmethod 
    def searchHandler(SessionID):
        
        try:
            conn_db=Connessione.Connessione()
            SearchResultService.SearchResultService.delete(conn_db.crea_cursore())
        finally:
            conn_db.esegui_commit()
            conn_db.chiudi_connessione()
        while True:
            query_ricerca = raw_input("\n\tInserire la stringa di ricerca (massimo 20 caratteri): ")
            if(len(query_ricerca) <= 20):
                break
            print("\n\tErrore lunghezza query maggiore di 20!")
        query_ricerca = Util.Util.riempi_stringa(query_ricerca, 20)
        stringa_da_trasmettere="FIND"+SessionID+query_ricerca
        print "Invio supernodo: "+stringa_da_trasmettere
        
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.connect((Util.IPSuperPeer, int(Util.PORTSuperPeer)) )
            sock.send(stringa_da_trasmettere.encode())
            
            #lettura e scrittura su db dei risultati della ricerca di un file 
            stringa_ricevuta=sock.recv(4)
            if(stringa_ricevuta!="AFIN"):
                print "Errore non ricevuto AFIN"
            else:
	    	stringa_ricevuta=sock.recv(3)
                print(stringa_ricevuta)
		occorenze_md5=int(stringa_ricevuta)
                print("occorenze md5: "+str(occorenze_md5))
		
                for i in range(0,occorenze_md5):
                        print("ciao contatore: "+str(i))
                        filemd5=sock.recv(16)
                        print("md5: "+filemd5)
			filename=sock.recv(100)
                        #elimino eventuali asterischi e spazi finali
                        filename=Util.Util.elimina_spazi_iniziali_finali(filename)
                        filename=Util.Util.elimina_asterischi_iniziali_finali(filename)
                        
                        print("file name: "+filename)
			occorenze_peer=int(sock.recv(3))
                        print("occorenze peer: "+str(occorenze_peer))
                        #print("Contatore: "+str(i)+"filemd5: "+filemd5+"filename: "+filename+" Occorenze Perr: "+str(occorenze_peer))
			for j in range(0,occorenze_peer):
				ipp2p=sock.recv(39)
				pp2p=sock.recv(5)
                                print("IPP2P"+ipp2p+"PP2P: "+pp2p )
				try:
            				conn_db=Connessione.Connessione()
            				SearchResultService.SearchResultService.insertNewSearchResult(conn_db.crea_cursore(), ipp2p, pp2p, filemd5, filename, "0000000000000000", 'T')
        			finally:
            				conn_db.esegui_commit()
            				conn_db.chiudi_connessione   
            sock.close()
            
        except Exception as e:
            print e
            print"Errore nel contattare il supernodo per ricerca file"
            

    @staticmethod
    def downloadFile():
        
        conn_db = Connessione.Connessione()
        searchResults = SearchResultService.SearchResultService.getSearchResultsDownload(conn_db.crea_cursore())
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()
        
        
        
        i = 0
        while i < len(searchResults):
            print("\t"+str(i + 1) + ".\t" + searchResults[i].filename + "\t"+searchResults[i].ipp2p + "\t" + searchResults[i].pp2p)
            i = i + 1
        
        #il valore di choice e' incrementato di uno
        choice = int(raw_input("\t  Scegliere il numero del peer da cui scaricare (0 annulla): ")) 
        if(choice > 0):
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) 
            sock.connect((searchResults[choice - 1].ipp2p, int(searchResults[choice - 1].pp2p)))
            sendingString = "RETR" + searchResults[choice - 1].filemd5
            #sock.send(sendingString.encode())
            sock.send(sendingString)

            receivedString = sock.recv(10)        
            if receivedString[0:4].decode() == "ARET":
                nChunk = int(receivedString[4:10].decode())            
                chunk = bytes()
                chunkCounter = 0

                file = open(Util.LOCAL_PATH + searchResults[choice - 1].filename, "wb")
                
                #inizializzo la variabile temporanea per stampre la percentuale
                tmp = -1
                print "\nDownloading...\t",
                
                while chunkCounter < nChunk:
                    receivedString = sock.recv(1024)
                    chunk = chunk + receivedString                

                    while True:
                        
                        #Un po' di piacere per gli occhi...
                        perCent = chunkCounter*100//nChunk
                        if(perCent % 10 == 0 and tmp != perCent):
                            if(tmp != -1):
                                print " - ",
                            print str(perCent) + "%",
                            tmp = perCent
                        
                        if len(chunk[:5]) >=  5:
                            chunkLength = int(chunk[:5])
                        else:
                            break

                        if len(chunk[5:]) >= chunkLength:
                            data = chunk[5:5 + chunkLength]
                            file.write(data)
                            chunkCounter = chunkCounter + 1
                            chunk = chunk[5 + chunkLength:]
                        else:
                            break

                file.close()
                print ""

            sock.close() 

            #controllo correttezza del download
            myMd5 = Util.Util.md5(Util.LOCAL_PATH + searchResults[choice - 1].filename)        
            if myMd5 != searchResults[choice - 1].filemd5:
                print("Errore nel download del file, gli md5 sono diversi!")  
        else:
            print("Annullato")
            
            
    #operazioni del peer che riguardano lato server
    
    @staticmethod
    def initServerSocket():
        
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((Util.HOST, Util.PORT))
        s.listen(5)
        return s
    
    @staticmethod
    def readSocket(clientSocket):
        
        stringa_ricevuta_server = clientSocket.recv(SIZE)        
        if stringa_ricevuta_server == "":
            print("Socket vuota")
        else:      
            print("Pacchetto ricevuto: " + stringa_ricevuta_server)
        return stringa_ricevuta_server
    
    #upload
    @staticmethod
    def uploadHandler(client, stringa_ricevuta_server):
        
        chunkLength = 1024
        filemd5 = stringa_ricevuta_server[4:20]
        
        try:
            conn_db = Connessione.Connessione()
            
            file = SharedFileService.SharedFileService.getSharedFileMD5(conn_db.crea_cursore(), filemd5)
            
            conn_db.esegui_commit()
            conn_db.chiudi_connessione()

            if os.stat(Util.LOCAL_PATH + file.filename).st_size % chunkLength == 0:
                nChunk = os.stat(Util.LOCAL_PATH + file.filename).st_size // chunkLength
            else:
                nChunk = (os.stat(Util.LOCAL_PATH + file.filename).st_size // chunkLength) + 1
            
            nChunk = str(nChunk).zfill(6)
            sendingString = "ARET".encode()
            sendingString = sendingString + nChunk.encode()
            
            openedFile = open(Util.LOCAL_PATH + file.filename, "rb")

            while True:
                chunk = openedFile.read(chunkLength)
                if len(chunk) == chunkLength:
                    sendingString = sendingString + str(chunkLength).zfill(5).encode()
                    sendingString = sendingString + chunk
                else:
                    sendingString = sendingString + str(len(chunk)).zfill(5).encode()
                    sendingString = sendingString + chunk
                    break
            
#            while True:
#                m = sendingString[:1024] 
#                i = i+1               
#                client.send(m)                    
#                if len(m) < 1024:
#                    break
#                sendingString = sendingString[1024:]
            client.sendall(sendingString)
            
            openedFile.close()
            
        except:
            print sys.exc_info()
            print("File not found!")
    
    @staticmethod
    def loginSuperpeer():
        conn_db = Connessione.Connessione()
        peer = PeerService.PeerService.insertNewPeer(conn_db.crea_cursore(), Util.HOST, Util.PORT)
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()
        
        return peer.sessionid
    
    @staticmethod
    def superNearSearchHandler():
        conn_db = Connessione.Connessione()
        pkt = PacketService.PacketService.insertNewPacket(conn_db.crea_cursore(), None)
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()
        
        sendingString = "SUPE" + pkt.idpacket + Util.HOST + Util.Util.adattaStringa(5, str(Util.PORT)) + Util.Util.adattaStringa(2, str(Util.SUPERNEARTTL))
        
        conn_db = Connessione.Connessione()
        vicini = []
        vicini = SuperNearService.SuperNearService.getSuperNears(conn_db.crea_cursore())
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()
        
        print("Avvio ricerca di supernodi vicini")
        i = 0
        while i < len(vicini):           
            try:
                print("Inoltro al vicino con Ip:" + vicini[i].pp2p + ", Porta:" + vicini[i].ipp2p)
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                sock.connect((vicini[i].ipp2p, int(vicini[i].pp2p)))
                sock.send(sendingString.encode())
            except:
                print("Il vicino " + vicini[i].ipp2p + " " + vicini[i].pp2p + " non e' online")
            i = i + 1
