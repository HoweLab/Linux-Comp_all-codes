"""caiman2Mat.py: takes a CNMF caiman object and saves
relevant data into a .mat file.
"""

#__author__      = "Benjamin Graham"
#__LastEdited__ = 2/24/23
from scipy.io import savemat
from caiman.utils.visualization import get_contours
import numpy as np
import os


def saveCaimain2Mat(estimates, saveLocation, outName, dims, totalTime, goodIdxs, badIdxs):

  fields = vars(estimates)
  matInfo ={}
  #dictionary of vars that we are actually interested in taking from the CNMF object 
  varsWeWant = {
          'C':'temporal_components', 
          'b':'bckgrnd_spatial', 
          'f':'temporal_bckgrnd_components', 
          'YrA':'residual_components', 
          'F_dff':'dFF',
          # 'idx_components':'good_components',
          # 'idx_components_bad':'bad_components',
          'SNR_comp':'SnR',
          'r_values':'rVals',
          'cnn_preds':'cnn'
          }
  
  #making the sparse matrix into a 3D matrix that matlab will actually be able to parse
  numRois = np.shape(estimates.A)[1]
  spatialComponents = np.zeros([dims[0], dims[1], numRois])
  for cROI in range(np.shape(estimates.A)[1]):
    #changed cROI - 1 to cROI
    roiArray = np.reshape(estimates.A[:,cROI].toarray(), dims, order='F')
    spatialComponents[:,:,cROI] = roiArray

  #using an internal caiman function to extract the contours of our ROIs
  caimanContours = get_contours(estimates.A, dims)

  #manually add a couple of variabeles to our matInfo dictionary
  matInfo['ica_segments'] = spatialComponents 
  matInfo['timeTaken'] = totalTime
  matInfo['ROIContours'] = caimanContours
  matInfo['good_components'] = goodIdxs
  matInfo['bad_components'] = badIdxs

  #loop through the vars we want and save the corresponding variables into our matInfo dictionary
  for cK in varsWeWant.keys():
    matInfo[varsWeWant[cK]] = fields[cK]
  #use the scipy.io function to save out a .mat file from a dicionary input variable
  savemat(os.path.join(saveLocation, outName + '.mat'), matInfo)

  return matInfo



  



  