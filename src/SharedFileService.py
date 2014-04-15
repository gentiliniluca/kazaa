import SharedFile

class SharedFileService:
    
    @staticmethod
    def insertNewSharedFile(database, filemd5, filename):
        
        try:
            sharedFile = SharedFileService.getSharedFile(database, filename)
        except:
            sharedFile = SharedFile.SharedFile(None, filemd5, filename)
            sharedFile.insert(database)
        
        return sharedFile
    
    @staticmethod
    def getSharedFile(database, filename):
        
        database.execute("""SELECT idsharedfile, filemd5, filename
                            FROM sharedfile
                            WHERE filename = %s""",
                            (filename))
        
        idsharedfile, filemd5, filename = database.fetchone()
        
        sharedFile = SharedFile.SharedFile(idsharedfile, filemd5, filename)
        
        return sharedFile
    
    @staticmethod
    def getSharedFileMD5(database, filemd5):
        
        database.execute("""SELECT idsharedfile, filemd5, filename
                            FROM sharedfile
                            WHERE filemd5 = %s""",
                            (filemd5))
        
        idsharedfile, filemd5, filename = database.fetchone()
        
        sharedFile = SharedFile.SharedFile(idsharedfile, filemd5, filename)
        
        return sharedFile
    
    @staticmethod
    def getSharedFiles(database, searchString):
        
        searchString = "%" + searchString.upper() + "%"
        
        database.execute("""SELECT idsharedfile, filemd5, filename
                            FROM sharedfile
                            WHERE filename LIKE %s""",
                            searchString)
        
        sharedFiles = []
        
        try:
            while True:
                idsharedfile, filemd5, filename = database.fetchone()
                sharedFile = SharedFile.SharedFile(idsharedfile, filemd5, filename)
                sharedFiles.append(sharedFile)
        except:
            pass
        
        return sharedFiles