import Connessione
import FileService
import NearService
import PacketService
import random
import socket
import SearchResult
import SearchResultService
import string
import Util

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL)

class Client:
    
    @staticmethod
    def visualizza_menu_principale():
        
        while True:
            print("\n************************\n*  1 - Ricerca File    *\n*  2 - Ricerca vicini  *\n*  3 - Carica File     *\n*  4 - Download File   *\n*  0 - Fine            *\n************************")
            out=raw_input("\n\tOperazione scelta: ")
            if(int(out) >= 0 and int(out) <= 4):
                break
            print("Valore inserito errato! (valore compreso tra 0 e 4)")
        
        return out
    
    @staticmethod
    def nearHandler():
        
        conn_db = Connessione.Connessione()
        packetid = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        pkt = PacketService.PacketService.insertNewPacket(conn_db.crea_cursore(), packetid)
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()
        
        ttl = Util.TTL
        
        stringa_da_trasmettere = "NEAR" + pkt.packetid + Util.HOST + "" + Util.Util.adattaStringa(5, str(Util.PORT)) + Util.Util.adattaStringa(2, str(ttl)) 
        #print("valore inviato: "+stringa_da_trasmettere)
        
        #lettura vicini da db
        conn_db = Connessione.Connessione()
        vicini = []
        vicini = NearService.NearService.getNears(conn_db.crea_cursore())
        
        i = 0
        while i < len(vicini):
            #print("****" +" "+vicini[i].pp2p + " "+vicini[i].ipp2p)
            try:
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                sock.connect((vicini[i].ipp2p, int(vicini[i].pp2p)))
                sock.send(stringa_da_trasmettere.encode())
            except:
                print("Il vicino "+vicini[i].ipp2p+" "+vicini[i].pp2p + " non e' online")
            i = i + 1
            
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()
        
    @staticmethod
    def downloadHandler():
        
        conn_db = Connessione.Connessione()
        searchResults = SearchResultService.SearchResultService.getSearchResults(conn_db.crea_cursore())
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
            
    @staticmethod
    def searchHandler():
        while True:
            query_ricerca = raw_input("\n\tInserire la stringa di ricerca (massimo 20 caratteri): ")
            if(len(query_ricerca) <= 20):
                break
            print("\n\tErrore lunghezza query maggiore di 20!")
                
        #query_ricerca = Util.Util.aggiungi_spazi_finali(query_ricerca, 20)
        query_ricerca = Util.Util.riempi_stringa(query_ricerca, 20)
        
        #print(query_ricerca)                
            
        #pulisco la tabella searchresult, questa operazione va fatta prima di ogni ricerca
        conn_db = Connessione.Connessione()
        SearchResultService.SearchResultService.delete(conn_db.crea_cursore())
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()            
        
        conn_db = Connessione.Connessione()
        packetid = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        pkt = PacketService.PacketService.insertNewPacket(conn_db.crea_cursore(), packetid)
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()
        ttl = Util.TTL 
        stringa_da_trasmettere = "QUER" + pkt.packetid + Util.HOST + "" + Util.Util.adattaStringa(5,str(Util.PORT)) + Util.Util.adattaStringa(2,str(Util.TTL)) + query_ricerca
        
        #print("stringa inviata dal client: "+stringa_da_trasmettere)
        
        conn_db = Connessione.Connessione()
        vicini = []
        vicini = NearService.NearService.getNears(conn_db.crea_cursore())
        i = 0
        while i < len(vicini):
            #print ("****" +" "+vicini[i].pp2p + " "+vicini[i].ipp2p)
            try:
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                sock.connect((vicini[i].ipp2p, int(vicini[i].pp2p)) )
                sock.send(stringa_da_trasmettere.encode())
            except:
                print("Il vicino "+vicini[i].ipp2p+" "+vicini[i].pp2p + " non e' online")
            i = i + 1
            
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()
            
    @staticmethod
    def addFile():
        conn_db = Connessione.Connessione()
        nomefile = raw_input("Inserire il nome del file: " + Util.LOCAL_PATH)
#        nomefile = Util.LOCAL_PATH + nomefile
        filemd5 = Util.Util.get_md5(Util.LOCAL_PATH + nomefile)
        print("md5: " + filemd5 + " nome: " + nomefile)
        nomefile = Util.Util.aggiungi_spazi_finali(nomefile,100)
        #nomefile = Util.Util.riempi_stringa(nomefile, 100)
        file = FileService.FileService.insertNewFile(conn_db.crea_cursore(), filemd5, nomefile)
        
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()
            
