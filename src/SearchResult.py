class SearchResult:
    
    def __init__(self, idsearchresult, ipp2p, pp2p, filemd5, filename, packetid):
        self.idsearchresult = idsearchresult
        self.ipp2p = ipp2p
        self.pp2p = pp2p 
        self.filemd5 = filemd5
        self.filename = filename 
        self.packetid = packetid            
        
    def insert(self, database):
        database.execute("""INSERT INTO searchresult
                            (ipp2p, pp2p, filemd5, filename, packetid)
                            VALUES (%s, %s, %s, %s, %s)""",
                            (self.ipp2p, self.pp2p, self.filemd5, self.filename, self.packetid))