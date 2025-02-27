

#__author__      = "Benjamin Graham"
#__LastEdited__ = 2/24/23

import os
import glob

def findMovs(rootDirs, pattern, skip_complete = False):

    """tifLookup.py:
    Function findMovs takes a list of rootDirs (or just one rootDir) and looks recursively for subfolders.
    Finds all files in subfolders that match the pattern input and returns a list of paths for all of those 
    tifs. Also makes sure that the tifs are greater than 5GB so should only pull processed movies. 
    Note that the input rootDirs MUST be a list ['my/path'] even if it is only one directory.

    Inputs:

    rootDirs = Type:List
    - directories to search all subfolders and files of
    pattern = String
    - Pattern that you want the files to match i.e. 'mc_reg.tif'

    Returns:
    
    bigList = Type: List
    -List of all the files that contained the pattern specified. Returned as lists inside of lists. 
    """

    bigList = []
    for cDir in range(len(rootDirs)):
        rootDir = rootDirs[cDir]

        folderList = []
        for path in glob.glob(f'{(rootDir)}/*/**/', recursive=True):
            folderList.append(path)

        # folderList = [folder for folder in files if os.path.isdir(os.path.join(rootDir, folder)) == True]
        for cFol in range(len(folderList)):
            filesIn = os.listdir(os.path.join(rootDir, folderList[cFol]))

            if skip_complete == False:

                for cF in range(len(filesIn)):
                    currentPath = os.path.join(rootDir, folderList[cFol], filesIn[cF])
                    fileSize = (os.path.getsize(currentPath))
                    fileSize /= 1024.0 ** 3
                    if pattern.lower() in filesIn[cF].lower() and fileSize > 5:
                        bigList.append([os.path.join(rootDir, folderList[cFol], filesIn[cF])])
            else:
                checkForCaiman = [True for file in filesIn if "caiman" in file]

                if len(checkForCaiman) == 0:
                    for cF in range(len(filesIn)):
                        currentPath = os.path.join(rootDir, folderList[cFol], filesIn[cF])
                        fileSize = (os.path.getsize(currentPath))
                        fileSize /= 1024.0 ** 3
                        if pattern.lower() in filesIn[cF].lower() and fileSize > 5:
                            bigList.append([os.path.join(rootDir, folderList[cFol], filesIn[cF])])
    return(bigList)