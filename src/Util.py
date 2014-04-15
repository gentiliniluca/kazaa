import hashlib

class Util:
    
    global HOST
    HOST = "fd00:0000:0000:0000:482b:92b3:8aec:1694"#1dd3:234b:b49a:d734"
    global PORT
    PORT = 3332
    
    global IPSuperPeer
    IPSuperPeer="fd00:0000:0000:0000:c521:ae1e:ea72:8fc0"
    
    global PORTSuperPeer
    PORTSuperPeer=8000
        
    global USERNAME
    USERNAME = "root"
    global PASSWORD
    PASSWORD = "lorenzo91"
    
    global TTL
    TTL = 2
    
    global USEMODE
    USEMODE=""
        
    global MAX_NEARS
    MAX_NEARS = 2
    
    global LOCAL_PATH #percorso file condivisi
    LOCAL_PATH = "/home/lorenzo/Desktop/kazaa/src/FileCondivisi/"
    
    @staticmethod
    def adattaStringa(lunghezzaFinale, stringa):
        
        ritorno = stringa
        for i in range(len(stringa), lunghezzaFinale):
            ritorno = "0" + ritorno
        return ritorno
    
    @staticmethod
    def md5(filename):
        
        md5 = hashlib.md5()
        file = open(filename, "rb")
        while True:
           data = file.read(1024)
           md5.update(data)
           
           if len(data) < 1024:
               break
           
        return md5.digest() 
    
    @staticmethod
    def riempi_stringa(stringa,lunghezza):
        return Util.aggiungi_asterischi_finali(stringa,lunghezza)
        #return Util.aggiungi_spazi_finali(stringa,lunghezza)
    
    @staticmethod
    def aggiungi_spazi_finali(stringa, lunghezza):
        
        i = len(stringa)
        while i < lunghezza:
            stringa = stringa + ' '
            i = i + 1
        return stringa
    
    @staticmethod
    def aggiungi_asterischi_finali(stringa, lunghezza):
        
        i = len(stringa)
        while i < lunghezza:
            stringa = stringa + '*'
            i = i + 1
        return stringa
    
    @staticmethod
    def elimina_spazi_iniziali_finali(stringa):
        
        ritorno = ""
        ritorno2 = ""
        lettera = False
        lettera2 = False
        for i in range (0, len(stringa)):
            if(stringa[i] != " " or lettera == True):
                ritorno = ritorno + stringa[i]
                lettera = True
       
        ritorno = ritorno[::-1]
    
        for i in range (0,len(ritorno)):
            if(ritorno[i]!=" " or lettera2==True):
                ritorno2=ritorno2+ritorno[i]
                lettera2 = True
    
        return ritorno2[::-1]
    
    @staticmethod
    def elimina_asterischi_iniziali_finali(stringa):
        
        ritorno = ""
        ritorno2 = ""
        lettera = False
        lettera2 = False
        for i in range (0, len(stringa)):
            if(stringa[i] != "*" or lettera == True):
                ritorno = ritorno + stringa[i]
                lettera = True
       
        ritorno = ritorno[::-1]
    
        for i in range (0,len(ritorno)):
            if(ritorno[i]!="*" or lettera2==True):
                ritorno2=ritorno2+ritorno[i]
                lettera2 = True
    
        return ritorno2[::-1]
    
    @staticmethod
    def get_md5(filename):
        md5 = hashlib.md5()
        with open(filename,"rb") as f:
            while True:
                data = f.read(1024)
                md5.update(data)
                if len(data) < 1024:
                    break
        md5_res = md5.digest()
        return md5_res
    
    
