import bokeh.plotting as bpl
import cv2
import glob
import logging
import matplotlib.pyplot as plt
import numpy as np
import os
import time as t
import datetime as dt
from findDict import getCaimanParams
from caiman2Mat import saveCaimain2Mat
from scipy.io import savemat
from bokeh.io import export_png

try:
    cv2.setNumThreads(0)
except():
    pass

try:
    if __IPYTHON__:
        # this is used for debugging purposes only. allows to reload classes
        # when changed
        get_ipython().magic('load_ext autoreload')
        get_ipython().magic('autoreload 2')
except NameError:
    pass

import caiman as cm
from caiman.motion_correction import MotionCorrect
from caiman.source_extraction.cnmf import cnmf as cnmf
from caiman.source_extraction.cnmf import params as params
from caiman.utils.utils import download_demo
from caiman.utils.visualization import plot_contours, nb_view_patches, nb_plot_contour
from caiman.summary_images import max_correlation_image, mean_image



# Runs entire caiman pipeline.

# Args:
# fnames:  list
# list containing paths to movie files

# paramDict: dictionary
# Dictionary containing all the parameters our caiman pipeline will need.

# selectComponents: bool
# Decides if we are saving out both good and bad components or just good (optional) -> default True

# saveImages: bool
# Decides if we save images into caiman output folder (optional) -> default True

# Returns:
# cnm2: caiman object
# Result of the caiman pipeline. Check the caiman docs for more info on accessing relevant variables.

#start our main function

def runCaimanPipeline(fnames, paramDict, selectComponents = True, saveImages = True, doMC = False, saveH5 = True):
    try:
    # if True:
        t1 = dt.datetime.now()
        timeStamp = str(t1.year)  + '_' + str(t1.month) + '_' + str(t1.day) + '_' + str(t1.hour) + '_' + str(t1.minute)
        #Setup parameters and files:
        fileSize = os.path.getsize(fnames[0]) / 1024 /1024 / 1024
        print("Defining parameters...")
        opts = params.CNMFParams(params_dict=paramDict)

        ###STARTS CLUSTERS 
        #%% start a cluster for parallel processing (if a cluster already exists it will be closed and a new session will be opened)
        if 'dview' in locals():
            cm.stop_server(dview=dview)
        c, dview, n_processes = cm.cluster.setup_cluster(
            backend='local', n_processes=None, single_thread=False)
        #%% restart cluster to clean up memory
        cm.stop_server(dview=dview)
        c, dview, n_processes = cm.cluster.setup_cluster(
            backend='local', n_processes=None, single_thread=False)

        ###START CNMF
        print("Starting CNMF...")
        startTime = t.time()
        #First pass of CNMF algo
        cnm1 = cnmf.CNMF(n_processes, params=opts, dview=dview)
        cnm1.fit_file(motion_correct=doMC)

        dataDir = os.path.dirname(fnames[0])
        dirFiles = os.listdir(dataDir)
        fileName = os.path.basename(fnames[0])[0:-4]


        #Create a folder where our outputs will live
        folderDir = os.path.join(dataDir, 'caimanOuputs_' + timeStamp)
        caimanFolder = os.mkdir(folderDir)

        # Get memmapfile path so we can use it and delete it after we used it
        mmap_inplace = False
        for file in dirFiles:
            if 'memmap' in file:
                memMapFilePath = os.path.join(dataDir, file)
                mmap_inplace = True
        if not mmap_inplace:
            # We still get the memmap file location even if 
            # they are not stored in place. This way code down streams don't need 
            # more conditional statements -LT 3/14/25
            memMapFilePath = cnm1.mmap_file

        #create a logging file where we still basic info about the file/runtime etc
        logging.basicConfig(filename=os.path.join(folderDir,fileName[0:-4] + 'LogFile'), encoding='utf-8', level=logging.ERROR, force=True)

        # %%capture
        #%% RE-RUN seeded CNMF on accepted patches to refine and perform deconvolution 
        # startTimeSecondsPass = t.start()
        Yr, dims, T = cm.load_memmap(memMapFilePath)

        images = np.reshape(Yr.T, [T] + list(dims), order='F')         
        #running into issues with memory when we are calculating the local correlations image on somewhat larger tifs
        #I think I need to figure out how to appropriately run caiman by chunking and having the results be combined at the end.
        # Cn = cm.local_correlations(images.transpose(1,2,0))

        #Second pass of CNMF Algo
        cnm2 = cnm1.refit(images, dview=dview)

        #This is component evaulation: Looking at rVal, Snr, and using the CNN model to determine what are good and bad components
        print("Starting component evaluation....")
        cnm2.estimates.evaluate_components(images, cnm2.params, dview=dview)
        badComponents = cnm2.estimates.idx_components_bad
        goodComponents = cnm2.estimates.idx_components

        #Save the good and bad components before we get rid of the bad components
        if saveImages == True:
            Cn = cm.local_correlations(images.transpose(1,2,0))
            Cn[np.isnan(Cn)] = 0
            plot = nb_plot_contour(Cn, cnm2.estimates.A[:, cnm2.estimates.idx_components], dims[0], dims[1])
            export_png(plot, filename=os.path.join(folderDir, 'maxCorrelationGoodComponents.png'))
            plot = nb_plot_contour(Cn, cnm2.estimates.A[:, cnm2.estimates.idx_components_bad], dims[0], dims[1])
            export_png(plot, filename=os.path.join(folderDir, 'maxCorrelationBadComponents.png'))

        #Only select the good components to go through to our final ROIs
        #just set the optional argument selectComponents = True in the function call to select your good components and 
        #get rid of the bad ones. For trouble shooting/param testing it is better to keep all your components.
        if selectComponents == True:
            cnm2.estimates.select_components(use_object=True)

        #%% Extract DF/F values
        #changed frames_window from 250 -> 500 this significantly improves the traces that we are pulling out. 
        cnm2.estimates.detrend_df_f(quantileMin=8, frames_window=500)
        endTime = t.time()
        totalTime = round(endTime - startTime) / 60
        stringVersion = str(totalTime)
        print("CNMF Finished, saving images...")
        print("Time taken:" + stringVersion)
        logging.critical('Time for: ' + fileName  + " = " + stringVersion + ", file size = " + str(fileSize))
        logging.critical(paramDict)

        if saveImages == True:
            ###SAVE OUT IMAGES AND MAT FILE
            avgProj = mean_image(fnames, dview = dview)


            plot = nb_plot_contour(avgProj, cnm2.estimates.A, dims[0], dims[1])
            export_png(plot, filename=os.path.join(folderDir, 'avgProjectionContours.png'))

            plot = nb_plot_contour(Cn, cnm2.estimates.A, dims[0], dims[1])
            export_png(plot, filename=os.path.join(folderDir, 'maxCorrelationProjectionContours.png'))

        dictVersionOfMat = saveCaimain2Mat(cnm2.estimates,folderDir, fileName + '_caimanEval_' + timeStamp,dims,totalTime, goodComponents, badComponents)

        #%% STOP CLUSTER and clean up log files
        cm.stop_server(dview=dview)
        log_files = glob.glob('*_LOG_*')
        for log_file in log_files:
            os.remove(log_file)
        # remove memory map files since they are huge, and strikingly although caiman put them in a folder
        # called 'temp' in 'caiman_data' they DONT ACTUALLY REMOVE THEM
        print(f"Trying to remove memmap file at location: %s."%(memMapFilePath))
        os.remove(memMapFilePath)
        #save out the correlation image into the CNMF object so we don't have to remake it/remake the memmap when we want to do other stuff later.
        # cnm2.Cn = Cn
        #save the CNMF object as an h5
        if saveH5:
            cnm2.save(os.path.join(folderDir, fileName + '_caimanEval_Python.hdf5'))

        return cnm2
    except:
    # else:
        cm.stop_server(dview=dview)
        raise Exception("Ran into a problem somewhere... Stopping the cluster")
        
