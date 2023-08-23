from xml.etree import ElementTree as ET
import hashlib

#Constants
OPEN = "Open"
NOTAFINDING =  "NotAFinding"
NOTAPPLICABLE = "Not_Applicable"
NOTREVIEWED = "Not_Reviewed"
VULN = 'VULN'
STIG_DATA = 'STIG_DATA'
VULN_ATTRIB = 'VULN_ATTRIBUTE'
VULN_NUM = 'Vuln_Num'
ATTRIB_DATA = 'ATTRIBUTE_DATA'
SI_DATA = 'SI_DATA'
SID_NAME = 'SID_NAME' 
TITLE = 'title'
SID_DATA = 'SID_DATA'
RELEASE_INFO = 'releaseinfo'
HOST_NAME = 'HOST_NAME'
HOST_IP = 'HOST_IP'
HOST_MAC = 'HOST_MAC'
HOST_FQDN = 'HOST_FQDN'
COMMENTS = 'COMMENTS'
STATUS = 'STATUS'

#Use ET to grab the XML data 
def getCKL(fileName: str) -> ET.ElementTree:
    return ET.parse(fileName)

#get function for nested data 
def getText(CKLRoot: ET.Element, targetParent: str, targetIndex: str, indexText: str, targetTag: str) -> str:
    for targetGroup in CKLRoot.iter(targetParent):
        if targetGroup.find(targetIndex).text == indexText:
            return targetGroup.find(targetTag).text
    raise Exception('Tag not found')

#update function for CKL VULN DATA
def updateVuln(root: ET.Element, vulnIDNum: str, update: str, targetAttribute: str) -> None:
    if update != '':
        update = update.strip()
        for level1 in root.iter(VULN):
            for level2 in level1.iter(STIG_DATA):
                if level2.find(VULN_ATTRIB).text == VULN_NUM:
                    if level2.find(ATTRIB_DATA).text == vulnIDNum:
                        if level1.find(targetAttribute).text != update:
                            level1.find(targetAttribute).text = update

#simple get for unique tags not recommended for non-uniques
def quickGet(CKLRoot: ET.Element, uniqueTagName: str) -> str:
    for target in CKLRoot.iter(uniqueTagName):
        return target.text
    raise Exception("CKL Element not found!")

#quick update function intended for unique tags - not for non-uniques
def quickUpdate(CKLRoot: ET.Element, uniqueTagName: str, updateText: str) -> None:
    for target in CKLRoot.iter(uniqueTagName):
        target.text = updateText
        break

#get function for nested data - returns none if the data isn't found
def getCKLData(CKLRoot: ET.Element, targetParent: str, targetIndex: str, indexText: str, targetTag: str) -> str:
    for targetGroup in CKLRoot.iter(targetParent):
        if targetGroup.find(targetIndex).text == indexText:
            return targetGroup.find(targetTag).text
    return None

#create dictionary for a single CKL file - used to generate a hash table
def createHashPair(cklFileName: str) -> dict:
    data = ET.parse(cklFileName)
    cklFileName = cklFileName.split('\\')[-1]
    cklRoot = data.getroot()
    stig = getCKLData(cklRoot, SI_DATA, SID_NAME, TITLE, SID_DATA)
    version = getCKLData(cklRoot, SI_DATA, SID_NAME, RELEASE_INFO, SID_DATA)
    cpName = quickGet(cklRoot, HOST_NAME)
    date = None
    if version != None:
        date = version.split(": ")
        date = date[-1]
    else:
        raise Exception('Hash cannot be created - Stig version no found')
    # print(f'cpName: {cpName} stig: {stig} date: {date}')
    toHash = cpName + stig + date
    stHash = hashlib.sha256(toHash.encode('utf-8')).hexdigest()
    # print(f'Testing!!! the hash is: {stHash}')
    return {'hash': stHash, 'cklfile': cklFileName}

#CKL status interpreter - takes "human input" and returns the exact word(s) used in a ckl file
def parseStatus(statusStr):
    statusStr = statusStr.lower()
    if 'not' in statusStr:
        if 'fin' in statusStr:
            return NOTAFINDING
        elif 'app' in statusStr:
            return NOTAPPLICABLE
        elif 'rev' in statusStr:
            return NOTREVIEWED
        else:
            return OPEN
    elif statusStr == 'na':
        return NOTAPPLICABLE
    elif statusStr == 'nf':
        return NOTAFINDING
    elif statusStr == 'nr':
        return NOTREVIEWED
    else:
        return OPEN