import sys
import os
import json

FILE_NAME_1="./usersData/WizzyWi"
FILE_NAME_2=""
COMBOLIST_DIRECTORY_SAVE_PATH="./comboLists/"
PREFIX=""
USERNAME1="Spaget"
USERNAME2="Dorito"


def ReadWriteSort(fileLists):
    #print("SPAGET")
    nwLines1=[]
    nwLines2=[]

    file1 = open(fileLists[0], 'r')
    Lines1 = file1.readlines()
    print(Lines1)
    
    for line in Lines1:
        nwLines1.append([line,USERNAME1]) #Change this so that it can identify user names using env variables or pulling from the datafiles
    file1.close()
    try:   
        file2 = open(fileLists[1], 'r')
        Lines2 = file2.readlines()
        file2.close()
        for line in Lines2:
            nwLines2.append([line,USERNAME2]) #Change this so that it can identify user names using env variables or pulling from the datafiles
    except:
        print("There was a problem reading the second file.")
    
    spaget=0
    for line in nwLines2:
        nwLines1.insert(spaget,line)
        #print(spaget)
        spaget=spaget+2
    #print(nwLines1)

    with open(COMBOLIST_DIRECTORY_SAVE_PATH+USERNAME1+"+"+USERNAME2+"COMBOLIST"+".csv", "w") as fp:
        for line in nwLines1:
            fp.write(line[0]+","+line[1]+"\n")
            #print(line[0]+","+line[1])
    fp.close()
    
def main():
    if len(sys.argv) == 2:
        print("Merging: "+sys.argv[1])
        dirList=os.listdir()
        #print(sys.argv)
        fileNameList=sys.argv[1].split(",")
        for vari in (fileNameList):
            vari.strip('"')
            #print(vari)
            if vari in dirList:
                a =0
            else:
                raise ValueError('File(s) does/do not exist')
        #print("spaget")
        ReadWriteSort(fileNameList)
    else:
        print("File names to merge not specified in command line args going with default test files:"+)

if __name__ == "__main__":
    main()
