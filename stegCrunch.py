#!/usr/bin/python3.6

import os, argparse, logging, subprocess, time, multiprocessing
from multiprocessing import Process, current_process

logging.basicConfig(level=logging.DEBUG, format='%(message)s')

"""
stegCrunch.py
Brute force attack against steganography files that were created with steghide.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

After some testing, there is no improvement with more than 2 threads. Also, after
looking online, the multiprocessing library may yield better results.
"""

#Setting up the options.
parser = argparse.ArgumentParser()

parser.add_argument("-s", "--stegfile", type=str, help="Target file.")
parser.add_argument("-w", "--wordfile", type=str, help="Word list file.")
parser.add_argument("-p", "--processes", type=int, help="# of threads to spool.")
parser.add_argument("-l", "--logging", help="Enable logging.", action="store_true")

arguments = parser.parse_args()
argStegFile = arguments.stegfile
argWordFile = arguments.wordfile
argProcesses = arguments.processes
argLogging = arguments.logging

globalStop = str()
##############################################################################################################

def wordListLoader():
    if os.path.exists(argWordFile) :
        logging.debug("Word file exists.")
        workingFile = open(argWordFile, encoding='ISO-8859-1')
        logging.debug("Word file loaded into memory.")
        wordList = workingFile.read().split() #Create a list of words from the word file.

        #The rest of this is honestly more for debugging purposes, but would I think it would be nice for the user to
        #be able to see.
        wordListStat = subprocess.check_output(["stat", argWordFile])
        wordListMemorySize = wordListStat.split()
        wordListMemorySize = wordListMemorySize[3].decode("utf-8")
        print("Word List: " + argWordFile + " ------>Loaded into memory: " + str(len(wordList)) + " words @ " + str(wordListMemorySize) + " Bytes")
        #time.sleep(3)
    else :
        print("Error: Path does not exist for word list.")
        exit(1)
    return wordList
###############################################################################################################

def crunch(passwdList, stegFile, threadNum, threadTotal):
    global globalStop
    while int(threadNum + 1) <= len(passwdList): #For each word in the list, try to extract data.
        #os.system("clear")
        proccessName = current_process().name
        print("Attempt #" + str(threadNum + 1) + "/" + str(len(passwdList)) + " with word \"" + str(passwdList[threadNum]) + "\" by " + str(proccessName))
        outputText = subprocess.run(["steghide", "extract", "-sf", stegFile, "-p", passwdList[threadNum]])
        #Need to check 'outputText' for exit code of '0' in order to know if steghide has succeeded.
        #I suspect this will cause a concurrency issue.
        #Thread2 is going beyond the bounds of the word list for some reason and will frequently cause an error.
        #logging.debug(outputText)

        #Will need to parse outputText for the return code.
        outputText = str(outputText)
        outputText = outputText.split()
        returnCode = list(outputText[-1])
        returnCode = returnCode[-2]

        if returnCode == "1" :
            threadNum += threadTotal
        elif returnCode == "0" :
            globalStop = "stop" #Tell the other threads to stop.
            print("Success with word \"" + str(passwdList[threadNum]) + "\"")
            return
        else :
            print("Unknown error code.")
            exit(1)

        if globalStop == "stop" : #If one thread tells another to stop, then stop.
            return

    return
###############################################################################################################


#Main##########################################################################################################

#First, check for logging.
if argLogging is True :
    logging.debug("Logging enabled.")
else :
    logging.disable(logging.CRITICAL)

#Next, check for other options.
if argStegFile is not None and argWordFile is not None : #Options and arguments were detected.
    logging.debug("Options and arguments detected.")

    if os.path.exists(argStegFile) :
        logging.debug("Steg file exists.")
        #Grab the word list.
        wordList = wordListLoader()
        logging.debug("Word list is ready as a Python list.")

        if argProcesses is not None : # If multi-processing was requested.
            logging.debug("Multiprocessing was requested: " + str(argProcesses) + " processes requested.")

            if multiprocessing.cpu_count() <= argProcesses : #A correct number of cores was requested.
                procs = [] #Create a list to contain the processes.

                if __name__ == "__main__" : #Occurs in main thread.
                    for p in range(argProcesses) : #Create the requested amount of processes.
                        startTime = time.time() #Start the clock.
                        process = Process(target=crunch, args=(wordList, argStegFile, p, argProcesses))
                        procs.append(process)
                        process.start()

                    for process in procs :
                        process.join()
            else :
                print("Error. Only " + str(multiprocessing.cpu_count()) + " cores available. " + str(argProcesses) +\
                      " threads were requested.")
        else : #No multithreading was requested.
            startTime = time.time() #Start the clock.
            crunch(wordList, argStegFile, 0, 1)

    else :
        print("Error: Steg file does not exist.")
else :
    print("Nope.")

stopTime = time.time()
totalTime = stopTime - startTime

print("Execution took: " + str(totalTime) + " seconds.")
exit(0)
