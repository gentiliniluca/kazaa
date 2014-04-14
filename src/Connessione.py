import MySQLdb
import Util


class Connessione:
    def __init__(self):
        try:
           
            self.db = MySQLdb.connect(host = "localhost", # your host, usually localhost
                                      user = Util.USERNAME, # your username
                                      passwd = Util.PASSWORD, # your password
                                      db = "kazaa") # name of the data base
        
        except Exception as e: 
            print e
            print("Errore crea db")
        
                           
                             
    def crea_cursore(self):
        try:
            cur = self.db.cursor()
        except Exception as e: 
            print e
            print("Errore crea cursore")
        return cur
        
        
    def esegui_commit(self):
        try:
            self.db.commit()
        except Exception as e: 
            print e
            print("Errore esegui commit")
            
            
    def chiudi_connessione(self):
        try:
            self.db.close()
        except Exception as e: 
            print e
            print("Errore chiudi connessione")
        