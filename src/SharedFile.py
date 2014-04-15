class SharedFile:
    def __init__(self, idsharedfile, filemd5, filename):
        self.idsharedfile = idsharedfile
        self.filemd5 = filemd5
        self.filename = filename
    
    def insert(self, database):
        
        database.execute("""INSERT INTO sharedfile
                            (filemd5, filename)
                            VALUES (%s, %s)""",
                            (self.filemd5, self.filename))
    
    def update(self, database):
        
        database.execute("""UPDATE sharedfile
                            SET filename = %s, filemd5 = %s
                            WHERE idsharedfile = %s""",
                            (self.filename, self.filemd5, self.idsharedfile))
    
    def delete(self, database):
        
        database.execute("""DELETE FROM sharedfile
                            WHERE idsharedfile = %s""",
                            (self.idsharedfile))
