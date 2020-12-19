import pysftp as sftp
import os

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
                              port=222,
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
    
#recursive remote directory & files listing (rcdl)   
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
    
    diffRemoveList = list(set(dirRemote)-set(dirCurrent))
    diffUploadList = list(set(dirCurrent)-set(dirRemote))
    #print(diffRemoveList)
    #print(diffUploadList)
    diffRemoveList.sort(reverse = True)
    diffUploadList.sort()
    #print('remove directory',diffRemoveList)
    #print('upload directory',diffUploadList)
    for item in diffUploadList:
        #print('makingdir')
        server.mkdir(item)        
    for item in diffRemoveList:
        
        item = item.replace(' ','\ ')
        #print('removing files',('rm -rf ./Documents/Synced'+item[1:len(item)]))
        #print('removingdir')
        server.execute('rm -rf ./Documents/Synced'+item[1:len(item)])
        #server.rmdir(item)

#compares files to copy files over if nonexistent in remote
#and deletes files if nonexistent in current.
def compareFiles(fileRemote,fileCurrent,server):
    diffRemoveList = list(set(fileRemote)-set(fileCurrent))
    diffUploadList = list(set(fileCurrent)-set(fileRemote))
    #print(diffRemoveList)
    #print(diffUploadList)
    #print(diffRemoveList)
    #print(diffUploadList)
    for item in diffUploadList:
        dire = os.path.split(item)[0]
        with server.cd(dire):
            server.put(item,preserve_mtime=True)

    for item in diffRemoveList:
        dire = os.path.split(item)[0]
        server.remove(item)

#called by "compareFiles," this function extracts the linux times
#from current file and its corresponding file using "os.stat"
#then replaces the remote file if the current file is newer.
def compareFileDates(filesRemote,filesCurrent,server):
    for fileRemote in filesRemote:
        if fileRemote in filesCurrent:
            fileCurrent = fileRemote
            dire = os.path.split(fileCurrent)[0]
            RFN = os.path.basename(fileRemote)
            with server.cd(dire):
                currentFileTime = int(os.stat(fileRemote).st_mtime)
                remoteFilesAttribute = server.listdir_attr()
                for remoteFileAttribute in remoteFilesAttribute:
                    if RFN == remoteFileAttribute.filename:
                        remoteFileTime = remoteFileAttribute.st_mtime

                if remoteFileTime < currentFileTime:
                    print('remote: '+str(remoteFileTime)+' || current: '+str(currentFileTime))
                    print('yeet')
                    server.put(fileCurrent,preserve_mtime=True)

def checkDownloading():
    #with server.cd('Documents/Synced/sync_app'):
    #    server.get('is_downloading.txt','sync_app/is_downloading.txt')
    f = open("sync_app/is_downloading.txt","r")
    downloadingValue = int(f.readline())
    if int(downloadingValue) == 1:
        return True
    elif int(downloadingValue) == 0:
        return False
    


def updatelog(server):
    f = open("sync_app/computer_info.txt","r")
    name = f.readline().split(' ')[1].replace('\n','')
    f = open("sync_app/recent_sync_log.txt","w+")
    f.write(name)
    f.close()
    with server.cd('sync_app'):
        server.put("sync_app/recent_sync_log.txt",preserve_mtime=True)
            
                    


def main():
    os.chdir('..')
    dVal = checkDownloading()
    #print(dVal)
    if dVal == False:
        print('starting')
        global remoteFiles
        global remoteDirectory
        srv = initializeServer()
        #dVal = False
        with srv.cd('Documents/Synced'):
            rcdl('.')
            print('finished recursive current directory & files listing for the first time')
            rrdl(srv,'.')
            print('finished recursive remote directory & files listing')
            compareDirectories(remoteDirectory,currentDirectory,srv)
            #print('remote directory',remoteDirectory)
            #print('current directory',currentDirectory)
            print('finished comparing directories')
            remoteFiles = []
            remoteDirectory = []
            rrdl(srv,'.')
            print('finished recursive current directory & files listing for the second time')
            compareFileDates(remoteFiles,currentFiles,srv)
            print('finished comparing file dates')
            compareFiles(remoteFiles,currentFiles,srv)
            print('finished comparing files')
            updatelog(srv)
            print('done')
    elif dVal == True:
        pass






main()

#rcdl('.')
#rrdl(initializeServer(),'Documents/Synced')
#server = initializeServer()

