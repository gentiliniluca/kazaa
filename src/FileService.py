import File
import Peer
#import sys

class FileService:
        
    @staticmethod
    def insertNewFile(database, sessionid, filemd5, filename):
        try:
            file = FileService.getFile(database, filemd5)            
            file.filename = filename            
            file.update(database)
            
            print("MD5 already registered. Filename changed: '" + file.filename + "'")
        except:
            pass
              
        try:
            file = File.File(filemd5, filename)            
            file.insert(database, sessionid)
        except:
            pass
    
    @staticmethod
    def getFile(database, filemd5):
        database.execute("""SELECT filemd5, filename
                            FROM file
                            WHERE filemd5 = %s""",
                            filemd5)
        
        filemd5, filename = database.fetchone()
        
        file = File.File(filemd5, filename)
        
        return file
    
    @staticmethod
    def getNCopy(database, filemd5):
        database.execute("""SELECT count(*)
                            FROM peer_has_file
                            WHERE file_filemd5 = %s""",
                            filemd5)
        count, = database.fetchone()
        return count
    
    @staticmethod
    def getFiles(database, searchString):
        searchString = "%" + searchString + "%"
        database.execute("""SELECT filename, filemd5, sessionid, ipp2p, pp2p
                            FROM file, peer, peer_has_file
                            WHERE file_filemd5 = filemd5 AND
                                  peer_sessionid = sessionid AND
                                  filename LIKE %s
                            ORDER BY filemd5, sessionid""",
                            searchString)
        
        #print database._last_executed
        
        try:
            i = -1
            files = []
            #peers = []
            previous_filemd5 = ""
            while True:
            
                filename, filemd5, sessionid, ipp2p, pp2p = database.fetchone()
                #print filename, filemd5, sessionid, ipp2p, pp2p
                
                if filemd5 != previous_filemd5:
                    files.append(File.File(filemd5, filename))
                    #print files[i].filemd5
                    #j = 0
                    #files[i].setPeers([])
                    previous_filemd5 = filemd5
                    i = i + 1
                
                #print len(files[i].peers)
                files[i].peers.append(Peer.Peer(sessionid, ipp2p, pp2p))
                #print len(files[i].peers)
                #print files[i].peers[j].sessionid
                #j = j + 1
        
        except:
            pass
            #print sys.exc_info()
            
        return files