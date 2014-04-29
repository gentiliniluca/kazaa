class SearchResult:
    
    def __init__(self, idsearchresult, ipp2p, pp2p, filemd5, filename, packetid, myResult):
        self.idsearchresult = idsearchresult
        self.ipp2p = ipp2p
        self.pp2p = pp2p 
        self.filemd5 = filemd5
        self.filename = filename 
        self.packetid = packetid 
        self.myResult = myResult           
        
    def insert(self, database):
        database.execute("""INSERT INTO searchresult
                            (ipp2p, pp2p, filemd5, filename, packetid, myResult)
                            VALUES (%s, %s, %s, %s, %s, %s)""",
                            (self.ipp2p, self.pp2p, self.filemd5, self.filename, self.packetid, self.myResult))