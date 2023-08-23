import csv
from datetime import date
import hashlib

#commonly needed and used column names for csvs generated by STIG Viewer
STIG = 'STIG'
NAME = 'Name'
IP = 'IPAddress'
MAC = 'MACAddress'
FQDN = 'Fully Qualified Domain Name'
STATUS = 'Status'
VULNID = 'Vuln ID'
COMMENTS = 'Comments'

#List of name, ip, and list name. Each entry must be unique.
#This means only 1 match between ip and name are allowed and only 1 match of the IP - Name pair with each 
# list name. It allows for splitting an all emcompassing list of combined stig csvs into multiple csvs
# or a list of lists
class STIGList:
    def __init__(self):
        self.leftSide = []
        self.rightSide = []
        self.checklistName = []
    
    #add a unique triplet - with TONS of checks. Returns True if there's an error. May change to raise exception later
    def add(self, leftVar: str, rightVar: str, listName: str) -> bool:
        if leftVar in self.leftSide or rightVar in self.rightSide:
            if leftVar in self.leftSide and rightVar in self.rightSide:
                if rightVar == self.rightSide[self.leftSide.index(leftVar)]:
                    if listName == self.checklistName[self.leftSide.index(leftVar)]:
                        return False
                    else:
                        count = 0
                        for item in self.checklistName:
                            if item == listName and leftVar == self.leftSide[count] and rightVar == self.rightSide[count]:
                                return False
                            else:
                                count += 1
                        self.leftSide.append(leftVar)
                        self.rightSide.append(rightVar)
                        self.checklistName.append(listName)
                        return False
                else:
                    # print(f'left: {leftVar}, right: {rightVar}, name: {listName} - Error here - inner loop')
                    return True
            else:
                # print(f'left: {leftVar}, right: {rightVar}, name: {listName} - Error here - outer loop')
                # print('Check the name of the machine make sure it is consistant')
                return True
        else:
            self.leftSide.append(leftVar)
            self.rightSide.append(rightVar)
            self.checklistName.append(listName)
            return False
    
    def toList(self) -> list:
        tempZip = zip(self.leftSide, self.rightSide, self.checklistName)
        listOut = []
        for item in tempZip:
            listOut.append(list(item))
        return listOut
    
#functions

#pull name from "properly" formatted stig column
def pullSTIGName(rowFromTrips: list) -> str:
    versionData = rowFromTrips[2].split(" :: ")
    return versionData[0]

#removing the CUI header if needed - may need to expand to other classifications
def prepData(data: list) -> list:
    foundInHeader = False
    foundInFooter = False
    for str in data[0]:
        if "CUI" in str:
            foundInHeader = True
            break
    for str in data[len(data)-1]:
        if "CUI" in str:
            foundInFooter = True
            break
    if foundInFooter:
        data.pop(len(data) - 1)
    if foundInHeader:
        data.pop(0)
    return data

#grab data from the csv file(s)
def getCSVData(fileName: str) -> list:
    file = open(fileName,"r")
    data = list(csv.reader(file, delimiter=","))
    file.close()
    data = prepData(data)
    return data

#get the column info for the csv
def getColumnNames(data: list) -> list:
    columnNames = data[0]
    return columnNames

#function to generate a dictionary/set with IP and Computer Name key pairs given lists of both
def createIPNamePairs(ipColumnNumber: int, nameColumnNumber: int, stigColumnNumber: int, headlessDataList: list) -> STIGList:
    if ipColumnNumber == -1 or nameColumnNumber == -1 or stigColumnNumber == -1:
        raise Exception("Column format error in source CSV")
    sList = STIGList()
    error = False
    for row in headlessDataList:
        error = sList.add(row[nameColumnNumber], row[ipColumnNumber], row[stigColumnNumber])
        if error:
            raise Exception("CSV Formatting Error!")
    return sList

#function to write a batch of files based on the list of triples -returns list of file locations and hashes
def splitFiles(folderLocation: str, splitData: STIGList, combinedCSVData: list, nameColumnNumber: int, stigColumnNumber: int, columnNames: list) -> list:
    fileList = []
    dateStamp = str(date.today())
    counter = 0
    splitData = splitData.toList()
    for row in splitData:
        fileName = folderLocation + '/' + row[0] + '-' + str(counter) + '-' + dateStamp + '.csv'
        fileList.append(fileName)
        with open(fileName, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(columnNames)
            for csvrows in combinedCSVData:
                if csvrows[nameColumnNumber] == row[0] and csvrows[stigColumnNumber] == row[2]:
                    writer.writerow(csvrows)
        counter += 1
    return fileList

#get a key by passing the column title
def getKeyByName(row: list, name: str) -> int:
    counter = 0
    for title in row:
        if name == title:
            return counter
        else:
            counter += 1
    raise Exception("Key not found!")

#check the csv column for uniformity - assumes that first row is the colum name
def checkIfUniform(data: list, key: int) -> bool:
    if len(data) < 2:
        raise Exception("Improperly formatted CSV: length < 2")
    val = data[1][key]
    row = 1
    while row < len(data):
        if val != data[row][key]:
            return False
        else:
            row += 1
    return True

#create dictionary for a single CSV file - UNUSED - WHY IS THIS HERE?
# def createCSVDict(csvFileName: str) -> dict:
#     data = getCSVData(csvFileName)
#     data = prepData(data)
#     csvFileName = csvFileName.split('\\')[-1]
#     nameIndex = getKeyByName(data, NAME)
#     STIGIndex = getKeyByName(data, STIG)
#     version = data[1][STIGIndex].split(" :: ")
#     stig = version[0]
#     date = version[1].split(": ")
#     date = date[-1]
#     cpName = data[1][nameIndex]
#     stHash = hash(cpName + stig + date)
#     return {'hash': stHash, 'csvfile': csvFileName}

#send in one row of a csv and get the hash to match the ckl
def getHashFromRow(dataRow: list, nameIndex: int, STIGIndex: int) -> str:
    version = dataRow[STIGIndex].split(" :: ")
    stig = version[0]
    date = version[1].split(": ")
    date = date[-1]
    cpName = dataRow[nameIndex]
    toHash = cpName + stig + date
    rowFromHash = hashlib.sha256(toHash.encode('utf-8')).hexdigest()
    # print(f'TESTING!!! the hash is: {rowFromHash}')
    return rowFromHash

#function to return a seperate list of data for each entry in the STIGList within a dict of lists.
#The dict keys are hashes that correspond to a hash table on the ckl side
#DO NOT USE - BUGGED
def splitData(splitData: STIGList, combinedCSVData: list, nameColumnNumber: int, stigColumnNumber: int, columnNames: list) -> dict:
    splitData = splitData.toList()
    # print(f'splitData = {splitData}')
    resultingDict = {}
    currentHash = None
    for row in splitData:
        found = False
        for csvrows in combinedCSVData:
            print(f'row[0] = {row[0]} --- row[2] = {row[2]}')
            if csvrows[nameColumnNumber] == row[0] and csvrows[stigColumnNumber] == row[2]:
                currentHash = getHashFromRow(csvrows, nameColumnNumber, stigColumnNumber)
                resultingDict[currentHash] = columnNames
                found = True
                break
        if found:
            for csvrows in combinedCSVData:
                if csvrows[nameColumnNumber] == row[0] and csvrows[stigColumnNumber] == row[2]:
                    resultingDict[currentHash].append(csvrows)
    print(f'result: {resultingDict}')
    return resultingDict