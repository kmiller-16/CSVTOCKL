import ckl
import csv
import glob
import yaml
import file_handler as fh
import hashlib

#check ckl folder
#load settings from yaml
currentDir, setupPath = fh.loadSettings()
with open(setupPath,'r') as settings:
    setupData = yaml.safe_load(settings)
if setupData['setup']['hasrun']:
    search = setupData['filepaths']['cklfolder'] + "/*.ckl"
    cklList = glob.glob(search)
    tablePath = setupData['filepaths']['hashtable']
    finalList = []
    counter = 0
    for files in cklList:
        if '.ckl' in files:
            finalList.append(files)
    if len(finalList) > 0:
        hashes = []
        for item in finalList:
            hashes.append(list(ckl.createHashPair(item).values()))
        with open(tablePath, 'w', newline='') as file:
            writer = csv.writer(file)
            for rows in hashes:
                writer.writerow(rows)
        #output location to the user... we're done
        print(f'Hash table written. Location: {tablePath}')
    else:
        print("No files to write")
else:
    print("Run setup first")