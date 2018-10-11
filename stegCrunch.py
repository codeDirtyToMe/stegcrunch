#!/usr/bin/python3.6

import os, argparse, logging, subprocess, time

logging.basicConfig(level=logging.DEBUG, format='(%asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.CRITICAL)

"""
stegCrunch.py
~~~~~~~~~~~~~
Originally, this was a shell script that quickly grew out of bash's abilities.
Also, the speed at which the script could execute was rather limited because
sed was having to pull the word list back into memory between every extraction 
attempt. 

The goal is to create a much faster executing version of my stegCrunch.sh script.
As it stands now, it seems to be processing atleast twice as fast as the original
shell script and I haven't yet added mult-threading.

Plans for multi-threading.
In order to avoid concurreny issues I should have the threads leap frog through 
the list of words. Although this may not work as I don't have that much experience
with mult-threading. I may have to work with ques. We'll see. 
"""

#Setting up the options.
parser = argparse.ArgumentParser()

parser.add_argument("-s", "--stegfile", type=str, help="Target file.")
parser.add_argument("-w", "--wordfile", type=str, help="Word list file.")

arguments = parser.parse_args()
argStegFile = arguments.stegfile
argWordFile = arguments.wordfile

def wordListLoader():
    if os.path.exists(argWordFile) :
        workingFile = open(argWordFile, encoding='ISO-8859-1')
        wordList = workingFile.read().split() #Create a list of words from the word file.

        #The rest of this is honestly more for debugging purposes, but would I think it would be nice for the user to
        #be able to see.
        wordListStat = subprocess.check_output(["stat", argWordFile])
        wordListMemorySize = wordListStat.split()
        wordListMemorySize = wordListMemorySize[3].decode("utf-8")
        print("Word List: " + argWordFile + " ------>Loaded into memory: " + str(len(wordList)) + " words @ " + str(wordListMemorySize) + " Bytes")
        time.sleep(3)
    else :
        print("Error: Path does not exist for word list.")
        exit(1)
    return wordList

def crunch(passwdList, stegFile): #Need to add mult-threading.
    for x in range(len(passwdList)): #For each word in the list, try to extract data.
        os.system("clear")
        print("Attempt #" + str(x) + " with word: " + str(passwdList[x]))
        outputText = subprocess.run(["steghide", "extract", "-sf", stegFile, "-p", passwdList[x]])
        logging.debug(outputText)
    return

def main():
    if argStegFile is not None and argWordFile is not None : #Options and arguments were detected.
        logging.debug("Options and arguments detected.")
        if os.path.exists(argStegFile) :
            crunch(wordListLoader(), argStegFile)
        else :
            print("Error: Steg file does not exist.")
    else :
        print("Nope.")

    return

main()
exit(0)