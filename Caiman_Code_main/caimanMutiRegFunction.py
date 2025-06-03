# imports
import caiman as cm
from caiman.base.rois import register_multisession
from caiman.utils import visualization
from caiman.utils.utils import download_demo
from matplotlib import pyplot as plt
import numpy as np
from caiman.source_extraction.cnmf.cnmf import load_CNMF
from caiman.mmapping import save_memmap
from scipy.sparse import csc_matrix
from caiman.utils.visualization import plot_contours, nb_view_patches, nb_plot_contour
import os
from scipy.io import savemat


def runMutiReg(cm_files,movie_files,mat_savename = 'multi_reg.mat',mat_savefolder = ''):
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
    # load caiman Eval result from provided cm_files
    sessionList = []
    new_cm_files = [] # fnames to save the new caiman eval files (added correlation)
    for cF in range(len(movie_files)):
        cm_file = cm_files[cF]
        movie_file = movie_files[cF]
        dataDir = os.path.dirname(movie_file)
        fileName = os.path.basename(movie_file)[0:-4]
        print('Preparing data for', movie_file)
        currentEstimate = load_CNMF(cm_file)
        sessionList.append(currentEstimate)
        currentMemMap = save_memmap([movie_file], base_name=fileName + 'mmapFile', order='C')
        print('Memory map, mem-map file saved at:',currentMemMap)

        #make the correlation image
        print('Calculating local correlation...')
        Yr, dims, T = cm.load_memmap(currentMemMap)
        images = np.reshape(Yr.T, [T] + list(dims), order='F')
        Cn = cm.local_correlations(images.transpose(1,2,0)) 
        #save it into the caiman object
        currentCNM = sessionList[cF]
        currentCNM.Cn = Cn

        # save h5 file:
        cm_savename = os.path.join(dataDir, cm_file[0:-5] + '_addLocalCorr.hdf5')
        print('Trying to save file: ',cm_savename)
        #resave h5 with the correlations image
        currentCNM.save(cm_savename)
        # save out the filename for future process
        new_cm_files.append(cm_savename)
        #should remove the memmapped file once the correlations imagee is made
        print('Deleting mem map file at:',currentMemMap)
        os.remove(os.path.join(dataDir ,currentMemMap))

    # after initial process and memory map, load the new caiman eval
    # files to a list (prepare data to multi-session register)
    CI = []
    spatialComps = []
    for cS in new_cm_files:
        currentSession = load_CNMF(cS)
        CI.append(currentSession.Cn)
        spatialComps.append(currentSession.estimates.A)


    A = [csc_matrix(A1/A1.sum(0)) for A1 in spatialComps]
    dims = [ci.shape for ci in CI]
    dims_comb = tuple(np.array(dims).max(axis=0))

    #this is going to do a lot of reshaping and padding because all the videos are 
    # not the same size a lot of the time
    masks = [np.reshape(A_.toarray(), dims_ + (-1,), order='F').transpose(2, 0, 1)
                for A_, dims_ in zip(A, dims)]
    masks = [np.pad(m, list(zip([0]*3,[0, *(np.array(dims_comb) - m.shape[1:])])),
                    'constant', constant_values=0) for m in masks]
    CI = [np.pad(ci, list(zip([0]*2, (np.array(dims_comb) - ci.shape))),
                'constant', constant_values=0) for ci in CI]

    A = [csc_matrix(m.transpose(1,2,0).reshape((-1, m.shape[0]), order='F')) for m in masks]

    # max threshold parameter before binarization (not totally sure what this means but 
    # seems like it is important)
    max_thr = 0.1
    # the actual line that does all of the registrations stuff
    spatial_union, assignments, matchings = register_multisession(A, dims_comb, CI, max_thr=max_thr)
    # This link could be helpful for understanding the outputs: 
    # https://caiman.readthedocs.io/en/master/core_functions.html#caiman.base.rois.register_multisession



    # Filter components by number of sessions the component could be found
    n_reg = len(cm_files)  # get only rois active in all sessions

    # Use number of non-NaNs in each row to filter out components that were 
    # not registered in enough sessions
    assignments_filtered = np.array(np.nan_to_num(
        assignments[np.sum(~np.isnan(assignments), axis=1) >= n_reg]), dtype=int)

    # Use filtered indices to select the corresponding spatial components
    spatial_filtered = A[0][:, assignments_filtered[:, 0]]

    # Plot spatial components of the selected components on the template of 
    # the last session
    mask_info = visualization.plot_contours(spatial_union, CI[-1])

    # saving out matfile of the muti-session-register result.
    matInfo = {}
    # matInfo['spatial_union'] = spatial_union # this seem to be the full spatial mask,
    #  maybe I don't need to save this.
    matInfo['Assignment'] = assignments
    matInfo['matchings'] = matchings
    matInfo['mask_info'] = mask_info
    matInfo['ref_imgs'] = CI
    matInfo['file_paths'] = movie_files
    # saving, by default will save to the parent of the folder of the last item in movielist.
    if mat_savefolder == '':
        mat_savefolder = os.path.join(dataDir,'..')
    savepath = os.path.join(mat_savefolder,mat_savename)
    print('Saving registeration result to:',savepath)
    savemat(savepath, matInfo)
    return matInfo
