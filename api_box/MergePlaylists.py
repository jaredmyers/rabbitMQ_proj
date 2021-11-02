import sys
import os
import json

def ReadWriteSort(fileLists):
    #print("SPAGET")
    nwLines1=[]
    nwLines2=[]

    file1 = open(fileLists[0], 'r')
    Lines1 = file1.readlines()
    print(Lines1)
    
    for line in Lines1:
        nwLines1.append([line,"user1"]) #Change this so that it can identify user names using env variables or pulling from the datafiles
    file1.close()
    try:   
        file2 = open(fileLists[1], 'r')
        Lines2 = file2.readlines()
        file2.close()
        for line in Lines2:
            nwLines2.append([line,"user2"]) #Change this so that it can identify user names using env variables or pulling from the datafiles
    except:
        print("There was a problem reading the second file.")
    
    spaget=0
    for line in nwLines2:
        nwLines1.insert(spaget,line)
        #print(spaget)
        spaget=spaget+2
    #print(nwLines1)

    with open("COMBOLIST.csv", "w") as fp:
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
        print("not enough arguments passed. Requires both csv names before proceeding")

if __name__ == "__main__":
    main()