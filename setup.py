import yaml
import os
import file_handler as fh

currentDir, setupPath = fh.loadSettings()
err = False

#Setup Folders - Data, Data/UpdatedCKLs, CSV, CKL
def createFolder(folder: str) -> bool:
    try:
        newPath = os.path.join(currentDir, folder)
        os.mkdir(newPath)
        return True #true if succeed
    except:
        print("There was an error trying to create the directory for script data and updated ckl storage.")
        print("Check the folder permissions and file structure for the directory in which you are trying to run")
        print("the scripts. Then try again.")
        return False #false if fail

def rollback(targetFolder: str) -> None:
    dir = os.path.dirname(__file__)
    dir = os.path.join(dir, targetFolder)
    if os.path.exists(dir):
        os.rmdir(dir)

try:
    with open(setupPath,'r') as settings:
        setupData = yaml.safe_load(settings)
        dataDir = setupData['setup']['folders']['data']
        csvDir = setupData['setup']['folders']['csv']
        cklDir = setupData['setup']['folders']['ckl']
        updateDir = setupData['setup']['folders']['updates']
except:
    print("Error accessing settings.yml. Aborting setup")
    err = True

if not err and createFolder(dataDir):
    currentDir = os.path.join(currentDir, dataDir)
    if createFolder(updateDir) and createFolder(cklDir) and createFolder(csvDir):
        print("Folder structure created. Updating configuration")
    else:
        print('Subfolder creation failed... rolling back setup')
        rollback(dataDir + "/" + updateDir)
        rollback(dataDir + "/" + cklDir)
        rollback(dataDir + "/" + csvDir)
        rollback(dataDir)
        err = True
if not err:
    try:
        with open(setupPath,'r') as file:
            settings = yaml.safe_load(file)
            currentDir = os.path.dirname(__file__)
            dataPath = currentDir + '/' + dataDir
            settings['filepaths']['datafolder'] = dataPath
            settings['filepaths']['cklfolder'] = dataPath + '/' + cklDir
            settings['filepaths']['csvfolder'] = dataPath + '/' + csvDir
            settings['filepaths']['updated'] = dataPath + '/' + updateDir
            settings['filepaths']['hashtable'] = dataPath + '/' + settings['filepaths']['hashtable']
            settings['setup']['hasrun'] = True
        with open(setupPath,'w') as file:    
            yaml.dump(settings,file)
    except:
        print("Error writing settings to file. Rolling back setup")
        rollback(dataDir + "/" + updateDir)
        rollback(dataDir + "/" + cklDir)
        rollback(dataDir + "/" + csvDir)
        rollback(dataDir)
        err = True
if not err:
    print(f'Setup complete... for the next step transfer ckl files to {dataDir}/{cklDir}')
    print("Then run the populate command to setup the hash table.")