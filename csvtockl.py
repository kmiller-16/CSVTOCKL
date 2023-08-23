import sys
import file_handler as fh
import ckl
import yaml
import sviewer_csv as svcsv
import os

VERSION = 0.3

path = os.path.dirname(__file__) + "/settings.yml"
setupData = None
hashTable = None

#update function - takes one target ckl and one list pulled from csv and uses the list to update the ckl
#update is stored in the specified location
def update(targetFile: str, updateFrom: list, folderLocation: str, colNames) -> None:
    #define location and name of the updated file
    updatedFileName = targetFile.split('/')
    updatedFileName = updatedFileName[-1]
    resultingFile = folderLocation + '/' + updatedFileName.replace(".ckl", "") + "-Updated.ckl"
    #prepare list keys
    fqdnKey = svcsv.getKeyByName(colNames, svcsv.FQDN)
    commentKey = svcsv.getKeyByName(colNames, svcsv.COMMENTS)
    ip_Key = svcsv.getKeyByName(colNames, svcsv.IP)
    macKey = svcsv.getKeyByName(colNames, svcsv.MAC)
    statusKey = svcsv.getKeyByName(colNames, svcsv.STATUS)
    name_Key = svcsv.getKeyByName(colNames, svcsv.NAME)
    vulnIDKey = svcsv.getKeyByName(colNames, svcsv.VULNID)
    #set default status to open -- if there's an interpretation error in the list - this will be the result.
    currentStatus = ckl.OPEN
    #prepping the ckl for operations
    cklData = ckl.getCKL(targetFile)
    root = cklData.getroot()
    #updates on the system info
    ckl.quickUpdate(root, ckl.HOST_NAME, updateFrom[0][name_Key])
    ckl.quickUpdate(root, ckl.HOST_IP, updateFrom[0][ip_Key])
    ckl.quickUpdate(root, ckl.HOST_MAC, updateFrom[0][macKey])
    ckl.quickUpdate(root, ckl.HOST_FQDN, updateFrom[0][fqdnKey])
    #updates on each vulnerability listed in the ckl that matches vulns in the given list
    for item in updateFrom:
        currentStatus = ckl.parseStatus(item[statusKey])
        ckl.updateVuln(cklData, item[vulnIDKey], item[commentKey], ckl.COMMENTS)
        ckl.updateVuln(cklData, item[vulnIDKey], currentStatus, ckl.STATUS)
        #writing changes
    cklData.write(resultingFile)

with open(path,'r') as settings:
    setupData = yaml.safe_load(settings)

    if not setupData['setup']['hasrun']:
        print('You must run setup first: setup.py')
    elif len(sys.argv) < 2:
        print('Syntax error. Usage: csvtockl.py [your.csv]')
    else:
        print(f'csv to ckl updater - Version:{VERSION} by K. Miller of IEX Inc.')
        print('Starting pre-checks...')
        allPaths = []
        allPaths.append(setupData['filepaths']['cklfolder'])
        allPaths.append(setupData['filepaths']['csvfolder'])
        allPaths.append(setupData['filepaths']['datafolder'])
        allPaths.append(setupData['filepaths']['hashtable'])
        allPaths.append(setupData['filepaths']['updated'])
        if not fh.checkPaths(allPaths):
            print('Invalid folder structure. Re-run setup.')
        else:
            err = False
            csvfile = sys.argv[1]
            location, isValid = fh.checkFile(csvfile, ".csv")
            if not isValid:
                print("CSV file not found. Check the path and try again.")
                Err = True
            elif location == "same":
                csvfile = os.path.dirname(__file__) + "/" + csvfile
            if not os.path.exists(setupData['filepaths']['hashtable']):
                print("NO HASH TABLE FOUND - re-run setup")
                err = True
            else:
                hashTable = setupData['filepaths']['hashtable']
            if not err:
                #convert hash table to list
                hashTableData =svcsv.getCSVData(hashTable)
                #prepare to split files
                csvData = svcsv.getCSVData(csvfile)
                columnNames = svcsv.getColumnNames(csvData)
                nameRow = svcsv.getKeyByName(columnNames, svcsv.NAME)
                ipRow = svcsv.getKeyByName(columnNames, svcsv.IP)
                stigRow = svcsv.getKeyByName(columnNames, svcsv.STIG)
                csvData.pop(0)
                stigList = svcsv.createIPNamePairs(ipRow, nameRow, stigRow, csvData)
                #we're ready to split files
                splitList = svcsv.splitFiles(setupData['filepaths']['datafolder'], stigList, csvData, nameRow, stigRow, columnNames)
                #splitList is a list of our split off csv files - we now use each file to update each ckl that matches the hash table
                for splitOffFile in splitList:
                    #we need to calculate hash first
                    singleCSV = svcsv.getCSVData(splitOffFile)
                    columnNames = svcsv.getColumnNames(singleCSV)
                    singleCSV.pop(0)
                    #possibly redundant, but I want this to work
                    nameRow = svcsv.getKeyByName(columnNames, svcsv.NAME)
                    stigRow = svcsv.getKeyByName(columnNames, svcsv.STIG)
                    #we have our hash
                    currentHash = svcsv.getHashFromRow(singleCSV[0], nameRow, stigRow)
                    for line in hashTableData:
                        if line[0] == currentHash:
                            target = setupData['filepaths']['cklfolder'] + '/' + line[1]
                            update(target, singleCSV, setupData['filepaths']['updated'], columnNames)
                #clean up temp csvs
                for fileToRemove in splitList:
                    print(f'Removing: {fileToRemove}')
                    os.remove(fileToRemove)