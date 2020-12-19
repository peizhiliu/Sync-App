import pysftp as sftp
import os
import shutil

currentDirectory = []
currentFiles = []
remoteDirectory = []
remoteFiles = []
toCurrentFiles = []
toRemoteFiles = []

 
def initializeServer():
    cnopts = sftp.CnOpts()
    cnopts.hostkeys = None
    try:
        srv = sftp.Connection(host="",
                              username="",
                              password="",
                              port=,
                              cnopts=cnopts)
    except:
        srv = sftp.Connection(host="",
                              username="",
                              password="",
                              cnopts=cnopts)
    return srv

#recursive current directory & files listing (rcdl)
def rcdl(path):
    directory = os.listdir(path)
    for item in directory:
        if 'sync_app' not in item:
            if os.path.isfile(os.path.join(path,item)):
                currentFiles.append(os.path.join(path,item))
            elif os.path.isdir(os.path.join(path,item)):
                currentDirectory.append(os.path.join(path,item))
                rcdl(os.path.join(path,item))
    
#recursive remote directory & files listing (rrdl)   
def rrdl(server,path):
    #with server.cd(path):
    directory = server.listdir(path)   
    for item in directory:
        if 'sync_app' not in item:
            if server.isfile(sftp.reparent(path,item)):
                remoteFiles.append(sftp.reparent(path,item))
            elif server.isdir(sftp.reparent(path,item)):
                remoteDirectory.append(sftp.reparent(path,item))
                rrdl(server,sftp.reparent(path,item))

#compares directories to add folders if nonexistent in remote
#and deletes directories if nonexistent in current. Directories
#are built from highest up, down via sorting alphabetically
def compareDirectories(dirRemote,dirCurrent,server):
    diffDownloadList = list(set(dirRemote)-set(dirCurrent))
    diffRemoveList = list(set(dirCurrent)-set(dirRemote))
    #print(diffRemoveList)
    #print(diffUploadList)
    diffRemoveList.sort(reverse = True)
    diffDownloadList.sort()
    print(diffRemoveList)
    for item in diffDownloadList:
        os.mkdir(item)        
    for item in diffRemoveList:
        shutil.rmtree(item)
        #server.rmdir(item)

#compares files to copy files over if nonexistent in remote
#and deletes files if nonexistent in current.
def compareFiles(fileRemote,fileCurrent,server):
    diffDownloadList = list(set(fileRemote)-set(fileCurrent))
    diffRemoveList = list(set(fileCurrent)-set(fileRemote))
    #print(diffRemoveList)
    #print(diffUploadList)
    for item in diffDownloadList:
        dire = os.path.split(item)[0]
        with server.cd(dire):
            server.get(os.path.basename(item),item,preserve_mtime=True)

    for item in diffRemoveList:
        os.remove(item)

#called by "compareFiles," this function extracts the linux times
#from current file and its corresponding file using "os.stat"
#then replaces the remote file if the current file is newer.
def compareFileDates(filesRemote,filesCurrent,server):
    for fileCurrent in filesCurrent:
        if fileCurrent in filesRemote:
            fileRemote = fileCurrent
            dire = os.path.split(fileCurrent)[0]
            RFN = os.path.basename(fileRemote)
            with server.cd(dire):
                currentFileTime = int(os.stat(fileRemote).st_mtime)
                remoteFilesAttribute = server.listdir_attr()
                for remoteFileAttribute in remoteFilesAttribute:
                    if RFN == remoteFileAttribute.filename:
                        remoteFileTime = remoteFileAttribute.st_mtime

                if remoteFileTime > currentFileTime:
                    server.get(RFN,fileCurrent,preserve_mtime=True)

def updateDownloadingBeginning(server):
    f = open("sync_app/is_downloading.txt","w+")
    f.write('1')
    f.close()
    with server.cd('Documents/Synced/sync_app'):
        server.put('sync_app/is_downloading.txt',preserve_mtime=True)

def updateDownloadingEnd(server):
    f = open("sync_app/is_downloading.txt","w+")
    f.write('0')
    f.close()
    with server.cd('Documents/Synced/sync_app'):
        server.put('sync_app/is_downloading.txt',preserve_mtime=True)


def checkLog(server):
    with server.cd('Documents/Synced/sync_app'):
        server.get('recent_sync_log.txt','sync_app/recent_sync_log.txt')
 
    f = open("sync_app/computer_info.txt","r")
    name = f.readline().split(' ')[1].replace('\n','')
    
    f = open("sync_app/recent_sync_log.txt","r")
    try:
        recentPCName = f.readline().replace('\n','')
    except:
        pass
    if name == recentPCName or recentPCName == '':
        return 0
    elif name != recentPCName and recentPCName != '':
        return 1


def updateLog(server):
    f = open("sync_app/recent_sync_log.txt","w+")
    f.write('')
    f.close()
    with server.cd('sync_app'):
        server.put("sync_app/recent_sync_log.txt",preserve_mtime=True)
                    


def main():
    
    os.chdir('..')
    global remoteFiles
    global remoteDirectory
    global currentFiles
    global currentDirectory
    srv = initializeServer()
    initialNum = checkLog(srv)
    #print(initialNum)
    if initialNum == 1:
        updateDownloadingBeginning(srv)
        with srv.cd('Documents/Synced'):
            rcdl('.')
            print('finished recursive current directory & files listing for the first time')
            rrdl(srv,'.')
            print('finished recursive remote directory & files listing')
            compareDirectories(remoteDirectory,currentDirectory,srv)
            print('finished comparing directories')
            currentFiles = []
            currentDirectory = []
            rcdl('.')
            print('finished recursive current directory & files listing for the second time')
            compareFileDates(remoteFiles,currentFiles,srv)
            print('finished comparing file dates')
            compareFiles(remoteFiles,currentFiles,srv)
            print('finished comparing files')
            updateLog(srv)
        updateDownloadingEnd(srv)


        
    elif initialNum == 0:
        pass


    '''global remoteFiles
    global remoteDirectory
    srv = initializeServer()
    dVal = checkDownloading(srv)
    #dVal = False
    if dVal == False:
        with srv.cd('Documents/Synced'):
            rcdl('.')
            rrdl(srv,'.')
            compareDirectories(remoteDirectory,currentDirectory,srv)
            remoteFiles = []
            remoteDirectory = []
            rrdl(srv,'.')
            compareFileDates(remoteFiles,currentFiles,srv)
            compareFiles(remoteFiles,currentFiles,srv)
            updatelog(srv)
    elif dVal == True:
        pass'''






main()

#rcdl('.')
#rrdl(initializeServer(),'Documents/Synced')
#server = initializeServer()

