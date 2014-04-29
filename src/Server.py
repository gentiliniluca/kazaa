import Connessione
import PeerService
import FileService
import PacketService
import SuperNearService
import SearchResultService
import os
import socket
import Util
import string
import sys
import random
import time

from signal import signal, SIGPIPE, SIG_DFL
from os.path import stat
signal(SIGPIPE, SIG_DFL)

class Server:
    
    global SIZE
    SIZE = 1024
    
    stringa_ricevuta_server = ""
    
    @staticmethod
    def initServerSocket():
        
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((Util.HOST, Util.PORT))
        s.listen(5)
        return s
    
    @staticmethod
    def expiredPacketHandler():
        
        conn_db = Connessione.Connessione()
        PacketService.PacketService.deleteExpiredPacket(conn_db.crea_cursore())
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()
        
    @staticmethod
    def readSocket(clientSocket):
        
        stringa_ricevuta_server = clientSocket.recv(SIZE)        
        if stringa_ricevuta_server == "":
            print("Socket vuota")
        else:      
            print("Pacchetto ricevuto: " + stringa_ricevuta_server)
        return stringa_ricevuta_server
    
    @staticmethod
    def superNearSearchHandler(receivedString, clientSocket):
        pktid = receivedString[4:20]
        ipp2p = receivedString[20:59]
        pp2p = receivedString[59:64]
        ttl = receivedString[64:66]
        
        print("\t->Operazione ricerca vicini da supernodo Ip: " + ipp2p + ", Porta: " + pp2p + ", TTL: " + ttl + " (pktID: " + pktid + ")")
        
        conn_db = Connessione.Connessione()
        try:
            pkt = PacketService.PacketService.getPacket(conn_db.crea_cursore(), pktid)
            conn_db.esegui_commit()
            conn_db.chiudi_connessione()   
            
        except:
            pkt = PacketService.PacketService.insertNewPacket(conn_db.crea_cursore(), pktid)
            conn_db.esegui_commit()
            conn_db.chiudi_connessione()                      
            
            #se TTL > 1 inoltro il pacchetto ricevuto anche ai vicini
            if(int(ttl) > 1):                
                print("\t->Inoltro messaggio ai vicini")                
                newTTL = int(ttl) - 1 
                
                conn_db = Connessione.Connessione()
                vicini = []
                vicini = SuperNearService.SuperNearService.getSuperNears(conn_db.crea_cursore())
                conn_db.esegui_commit()
                conn_db.chiudi_connessione()    
                  
                i = 0
                while i < len(vicini):
                    if(vicini[i].ipp2p != ipp2p and vicini[i].pp2p != pp2p):
                        print("\t\t->Inoltro al vicino con Ip:" + vicini[i].pp2p + ", Porta:" + vicini[i].ipp2p)
                        
                        try:
                            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                            sock.connect((vicini[i].ipp2p, int(vicini[i].pp2p)))
                            sendingString = "SUPE" + pktid + ipp2p + Util.Util.adattaStringa(5, str(pp2p)) + Util.Util.adattaStringa(2,str(newTTL))
                            sock.send(sendingString.encode())                           
                        
                        except:
                            print("\t\t->Il vicino con Ip:" + vicini[i].ipp2p + ", Porta:" + vicini[i].pp2p + " non e' online")
                    
                    i = i + 1
                    
            #in ogni caso rispondo alla richiesta
            sendingString = "ASUP" + pktid + Util.HOST + Util.Util.adattaStringa(5, str(Util.PORT))
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.connect((ipp2p, int(pp2p)))
            sock.send(sendingString)
            sock.close()
            
        print("\t->OK")

    @staticmethod
    def superNearSearchResultHandler(receivedString):
        pktid = receivedString[4:20]
        ipp2p = receivedString[20:59]
        pp2p = receivedString[59:64]
        
        print("\tOperazione inserimento nuovo supernodo vicino. Ip: " + ipp2p + ", Porta: " + pp2p)
        
        conn_db = Connessione.Connessione()
        
        try:
            superNear = SuperNearService.SuperNearService.insertNewSuperNear(conn_db.crea_cursore(), ipp2p, pp2p)
            print("\t->OK")
        except:
            print("\t->Inserimento di vicino non effettuato")
        finally:
            conn_db.esegui_commit()
            conn_db.chiudi_connessione()       
    
    @staticmethod
    def loginHandler(receivedString, clientSocket):
        ipp2p = receivedString[4:43]
        pp2p = receivedString[43:48]
        print("\tOperazione Login. Ip: " + ipp2p + ", Porta: " + pp2p)

        conn_db = Connessione.Connessione()
        peer = PeerService.PeerService.insertNewPeer(conn_db.crea_cursore(), ipp2p, pp2p)
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()
        sessionID = peer.sessionid

        sendingString = "ALGI" + sessionID
        print("\t->Restituisco: " + sendingString)
        clientSocket.send(sendingString)
        print("\t->OK")
        
    @staticmethod
    def logoutHandler(receivedString, clientSocket):
        sessionID = receivedString[4:20]
        print("\tOperazione LogOut. SessionID: " + sessionID)
    
        conn_db = Connessione.Connessione()
        peer = PeerService.PeerService.getPeer(conn_db.crea_cursore(), sessionID)
        count = PeerService.PeerService.getCountFile(conn_db.crea_cursore(), sessionID)
        peer.delete(conn_db.crea_cursore())
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()    
    
        sendingString = "ALGO" + Util.Util.adattaStringa(3, str(int(count))) 
        print("\t->Restituisco: " + sendingString)
        clientSocket.send(sendingString)
        print("\t->OK")
        
    @staticmethod
    def addFileHandler(receivedString):
        sessionID = receivedString[4:20]        
        fileMD5 = receivedString[20:36]        
        fileName = receivedString[36:136]      
        print ("\tOperazione AddFile. SessionID: " + sessionID + ", MD5: " + fileMD5 + ", Nome: " + fileName)
    
        conn_db = Connessione.Connessione()
        FileService.FileService.insertNewFile(conn_db.crea_cursore(), sessionID, fileMD5, fileName.upper())
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()
        print("\t->OK")
        
    @staticmethod
    def deleteFileHandler(receivedString):
        sessionID = receivedString[4:20]
        fileMD5 = receivedString[20:36]
        print("\tOperazione DeleteFile. SessionID: " + sessionID + ", MD5: " + fileMD5)

        conn_db = Connessione.Connessione()
        file = FileService.FileService.getFile(conn_db.crea_cursore(), fileMD5)
        file.delete(conn_db.crea_cursore(), sessionID)
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()
        print("\t->OK")     
        
    @staticmethod
    def fileSearchHandler(receivedString):        
        pktid = receivedString[4:20]
        ipp2p = receivedString[20:59]
        pp2p = receivedString[59:64]
        ttl = receivedString[64:66]
        ricerca_con_spazi = receivedString[66:86]
        ricerca = Util.Util.elimina_spazi_iniziali_finali(ricerca_con_spazi)        
        
        print("\tOperazione ricerca file da supernodo Ip: " + ipp2p + ", Porta: " + pp2p + ", TTL: " + ttl + " (pktID: " + pktid + ")")
        print("\t->Ricercato: " + ricerca)
        conn_db = Connessione.Connessione()
        try:
            pkt = PacketService.PacketService.getPacket(conn_db.crea_cursore(), pktid)
            conn_db.esegui_commit()
            conn_db.chiudi_connessione()   
            
        except:
            pkt = PacketService.PacketService.insertNewPacket(conn_db.crea_cursore(), pktid)
            conn_db.esegui_commit()
            conn_db.chiudi_connessione()                      
            
            #se TTL > 1 inoltro il pacchetto ricevuto anche ai vicini
            if(int(ttl) > 1):                
                print("\t->Inoltro messaggio ai vicini")                
                newTTL = int(ttl) - 1 
                
                conn_db = Connessione.Connessione()
                vicini = []
                vicini = SuperNearService.SuperNearService.getSuperNears(conn_db.crea_cursore())
                conn_db.esegui_commit()
                conn_db.chiudi_connessione()    
                  
                i = 0
                while i < len(vicini):
                    if(vicini[i].ipp2p != ipp2p and vicini[i].pp2p != pp2p):
                        print("\t\t->Inoltro al vicino con Ip:" + vicini[i].pp2p + ", Porta:" + vicini[i].ipp2p)
                        
                        try:
                            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                            sock.connect((vicini[i].ipp2p, int(vicini[i].pp2p)))
                            sendingString = "QUER" + pktid + ipp2p + Util.Util.adattaStringa(5, str(pp2p)) + Util.Util.adattaStringa(2,str(newTTL)) + ricerca_con_spazi
                            sock.send(sendingString.encode())                           
                        
                        except:
                            print("\t\t->Il vicino con Ip:" + vicini[i].ipp2p + ", Porta:" + vicini[i].pp2p + " non e' online")
                    
                    i = i + 1     
            
            #in ogni caso rispondo con l'elenco dei file del mio cluster
            conn_db = Connessione.Connessione()
            files = []
            files = FileService.FileService.getFiles(conn_db.crea_cursore(), ricerca)
            conn_db.esegui_commit()
            conn_db.chiudi_connessione()
            
            i = 0        
            while i < len(files):
                j = 0
                while j < len(files[i].peers):                 
                    sendingString = "AQUE" + pktid + files[i].peers[j].ipp2 + Util.Util.adattaStringa(5, files[i].peers[j].pp2p) + files[i].filemd5 + Util.Util.adattaStringa(100, files[i].filename)
                    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                    sock.connect((ipp2p, int(pp2p)))
                    sock.send(sendingString)
                    sock.close()                        
                    
                    j = j + 1
                i = i + 1 
    
    @staticmethod
    def fileSearchResultHandler(receivedString):                
        pktid = receivedString[4:20]
        ipp2p = receivedString[20:59]
        pp2p = receivedString[59:64]
        filemd5 = receivedString[64:80]
        filename = receivedString[80:180]
        
        print("\tRicevuto nuovo risultato di ricerca da Ip: " + ipp2p + ", Porta: " + pp2p + ", MD5: " + filemd5 + ", Nome File: " + filename + " (pktid: " + pktid + ")")
        
        filename = Util.Util.elimina_spazi_iniziali_finali(filename)
        
        conn_db = Connessione.Connessione()
        sr = SearchResultService.SearchResultService.insertNewSearchResult(conn_db.crea_cursore(), ipp2p, pp2p, filemd5, filename, pktid, 'F')
        
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()
        
        print("\t->OK")
        
    @staticmethod
    def fileSearchRequestHandler(receivedString, clientSocket): 
        sessionID = receivedString[4:20]
        searchString = receivedString[20:40] 
        
        searchString=Util.Util.elimina_spazi_iniziali_finali(searchString)
        searchString=Util.Util.elimina_asterischi_iniziali_finali(searchString)
        
        print("\tRichiesta ricerca file dal peer SessionID: " + sessionID + ", Ricerca: " + searchString)         
        
        conn_db = Connessione.Connessione()        
        pkt = PacketService.PacketService.insertNewPacket(conn_db.crea_cursore(), None)
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()
        
        ttl = Util.TTL 
        
        sendingString = "QUER" + pkt.idpacket + Util.HOST + Util.Util.adattaStringa(5,str(Util.PORT)) + Util.Util.adattaStringa(2,str(ttl)) + searchString
        
        conn_db = Connessione.Connessione()
        vicini = []
        vicini = SuperNearService.SuperNearService.getSuperNears(conn_db.crea_cursore())
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()
        
        print("\t->Avvio ricerca su supernodi vicini")
        i = 0
        while i < len(vicini):           
            try:
                print("\t->Inoltro al vicino con Ip:" + vicini[i].pp2p + ", Porta:" + vicini[i].ipp2p)
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                sock.connect((vicini[i].ipp2p, int(vicini[i].pp2p)))
                sock.send(sendingString.encode())
            except:
                print("\t->Il vicino " + vicini[i].ipp2p + " " + vicini[i].pp2p + " non e' online")
            i = i + 1  
        
        print("\t->Attesa dei risultati...")
        time.sleep(Util.SLEEPTIME)
        
        conn_db = Connessione.Connessione()
        searchResults = SearchResultService.SearchResultService.getSearchResults(conn_db.crea_cursore(), pkt.idpacket, searchString)
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()
        
        print("\t->Trovati " + str(len(searchResults)) + " risultati. Invio al peer...")
        
        sendingString = "AFIN" + Util.Util.adattaStringa(3, str(len(searchResults)))
        
        i = 0
        while i < len(searchResults):
            sendingString = sendingString + searchResults[i].filemd5

            sendingString = sendingString + Util.Util.aggiungi_spazi_finali(searchResults[i].filename, 100)
            
            sendingString = sendingString + Util.Util.adattaStringa(3, str(len(searchResults[i].peers)))
            
            j = 0
            while j < len(searchResults[i].peers):
                sendingString = sendingString + searchResults[i].peers[j].ipp2p
                sendingString = sendingString + searchResults[i].peers[j].pp2p
                
                j = j + 1
            i = i + 1
            
        clientSocket.send(sendingString)
        
        print("\t->OK")