import Connessione
import random
import socket
import string
import Util
import SharedFile
import SharedFileService


from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL)

class Client:
    
    @staticmethod
    def visualizza_menu_principale():
        
        while True:
            if(Util.USEMODE=="PEER"):
                print("\n************************\n*  1 - Ricerca File    *\n*  2 - Login           *\n*  3 - Carica File     *\n*  4 - Download File   *\n*  5 - Rimuovi File    *\n*  6 - Logout          *\n*  0 - Fine            *\n************************")
            else:
                print("\n************************\n*  1 - Ricerca File    *\n*  2 - Carica File     *\n*  3 - Download File   *\n*  4 - Rimuovi File    *\n*  0 - Fine            *\n************************")
            out=raw_input("\n\tOperazione scelta: ")
            if(Util.USEMODE=="PEER" and (int(out) >= 0 and int(out) <= 6 ) or Util.USEMODE=="SUPERPEER" and(int(out) >= 0 and int(out) <= 4) ):
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
            risposta=sock.recv(21)
            print(risposta)
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
        print(SessionID+"nel logout")
        if(SessionID != "" and SessionID != "0000000000000000"):
            stringa_da_trasmettere="LOGO"+SessionID
            print("str da trasmeteer"+stringa_da_trasmettere)
            try:
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                sock.connect((Util.IPSuperPeer, int(Util.PORTSuperPeer) ))
                sock.send(stringa_da_trasmettere.encode())
                sock.close()
            except Exception as e:
                print e
                print "Errore logout"
        return ""
    
    
    @staticmethod
    def addFile(SessionID):
        nomefile=""
        filemad5=""
        
        #aggiungo file nella tabella del peer SharedFile
        try:
            conn_db = Connessione.Connessione()
            nomefile = raw_input("Inserire il nome del file: " + Util.LOCAL_PATH)
            filemd5 = Util.Util.get_md5(Util.LOCAL_PATH + nomefile)
            print("md5: " + filemd5+"lunghezza: "+str(len(filemd5))+ "nome: " + nomefile)
            file = SharedFileService.SharedFileService.insertNewSharedFile(conn_db.crea_cursore(), filemd5, nomefile)
            
        except Exception as e:
            print e
            print("Errore aggiunta file")
        
        finally:
            conn_db.esegui_commit()
            conn_db.chiudi_connessione()
        
        #formatto e invio stringa di aggiunta file nel superpeer    
        try:
            #nomefile = Util.Util.aggiungi_spazi_finali(nomefile,100)
            stringa_da_inviare="ADFF"+SessionID+filemd5+nomefile
            print(stringa_da_inviare)
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