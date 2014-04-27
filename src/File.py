class File:
    def __init__(self, filemd5, filename):
        self.filemd5 = filemd5
        self.filename = filename
        self.peers = []
    
    def insert(self, database, sessionid):
        try:
            database.execute("""INSERT INTO file
                                (filemd5, filename)
                                VALUES (%s, %s)""",
                                (self.filemd5, self.filename))
        except:
            pass

        try:
            database.execute("""INSERT INTO peer_has_file
                                (peer_sessionid, file_filemd5)
                                VALUES
                                (%s, %s)""",
                                (sessionid, self.filemd5))
        except:
            pass
    
    def update(self, database):
        
        database.execute("""UPDATE file
                            SET filename = %s
                            WHERE filemd5 = %s""",
                            (self.filename, self.filemd5))
    
    def delete(self, database, sessionid):
        
        try:
            database.execute("""DELETE FROM peer_has_file
                                WHERE peer_sessionid = %s AND file_filemd5 = %s""",
                                (sessionid, self.filemd5))
        except:
            print("File non condiviso da questo peer. Nessuna cancellazione effettuata.")
            pass
        
        try:
            database.execute("""DELETE FROM file
                                WHERE filemd5 = %s""",
                                (self.filemd5))
        except:
            pass