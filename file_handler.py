import csv
import glob
import os

#get list of files in the given dir 
def listFiles(searchString: str) -> list:
    files = glob.glob(searchString)
    filesOut = []
    for item in files:
        filesOut.append(item.split('\\')[-1]) #remove dir info
    return filesOut

#get list with full path for each entry
def listFilesFull(searchString: str) -> list:
    files = glob.glob(searchString)
    filesOut = []
    for item in files:
        filesOut.append(item)
    return filesOut

# match lists by hash allowing a bulk update process of CSV => CKL
def hashMatch(CKLHashDicts: list, CSVHashDicts: list) -> list:
    matchedList = []
    if len(CKLHashDicts) >= len(CSVHashDicts):
        for dict1 in CKLHashDicts:
            for dict2 in CSVHashDicts:
                if dict1.get('hash') in dict2.values():
                    matchedList.append({'hash': dict1.get('hash'), 'cklfile': dict1.get('cklfile'), 'csvfile': dict2.get('csvfile')})
                    break
    else:
        for dict1 in CSVHashDicts:
            for dict2 in CKLHashDicts:
                if dict1.get('hash') in dict2.values():
                    matchedList.append({'hash': dict1.get('hash'), 'cklfile': dict2.get('cklfile'), 'csvfile': dict1.get('csvfile')})
                    break
    return matchedList

#writing hash table to file 
def writeHashTable(tableList: str, hashTableFile: str) -> None:
    with open(hashTableFile, 'w', newline='') as file:
        writer = csv.writer(file)
        for entry in tableList:
            writer.writerow(entry.values())

def checkPaths(paths: list) -> bool:
    for path in paths:
        if not os.path.exists(path):
            print(f"Path: {path} did not check out!")
            return False
    return True

def checkFile (file: str, extension: str) -> tuple[str,bool]:
    if extension not in file:
        return "invalid", False
    if "/" in file or "\\" in file:
        return "full", os.path.exists(file)
    else:
        return "same", os.path.exists(os.path.dirname(__file__) + "/" + file)
    
def loadSettings() -> tuple[str, str]:
    currentDir = os.path.dirname(__file__)
    setupPath = os.path.join(currentDir, "settings.yml")
    return(currentDir, setupPath)