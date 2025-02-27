"""findDict.py: 

Args:
fnames:  list
list containing paths to movie files

paramType: string
String specifying which dictionary you want to access ('brenna20', 'gabi20' -> can also do 40 if needed)

userSelect: bool
Set to false if you want to use a default dicionary (optional) -> default True -> accesses our predefined user dicitonaries

userInput: bool
Set to True if you want to use optional inputs to redefine parameters in our set dictionaries(optional) -> default False

Returns:
paramDict: Dictionary
Dictionary containing all the parameters we will use for our caiman pipeline.
"""

#__author__      = "Benjamin Graham"
#__LastEdited__ = 2/24/23

def getCaimanParams(fnames, paramType = '', userSelect = True, userInput = False, **Optionalparams):
    # dataset dependent parameters
    fr = 31                             # imaging rate in frames per second
    decay_time = 0.4                    # length of a typical transient in seconds

    # parameters for source extraction and deconvolution
    p = 2                       # order of the autoregressive system
    gnb = 2                     # number of global background components
    merge_thr = 0.60            # merging threshold, max correlation allowed
    rf = 25                     # half-size of the patches in pixels. e.g., if rf=25, patches are 50x50
    stride_cnmf = 14             # amount of overlap between the patches in pixels
    K = 4                       # number of components per patch
    gSig = [6, 5]               # expected half size of neurons in pixels
    method_init = 'greedy_roi'  # initialization method (if analyzing dendritic data using 'sparse_nmf')
    ssub = 2                    # spatial subsampling during initialization
    tsub = 2                    # temporal subsampling during intialization

    # parameters for component evaluation
    min_SNR = 2.0               # signal to noise ratio for accepting a component
    rval_thr = 0.80              # space correlation threshold for accepting a component
    cnn_thr = 0.90              # threshold for CNN based classifier
    cnn_lowest = 0.30 # neurons with cnn probability lower than this value are rejected

    defaultDict = {'fnames': fnames,
            'fr': fr,
            'decay_time': decay_time,
            'p': p,
            'nb': gnb,
            'rf': rf,
            'K': K, 
            'gSig': gSig,
            'stride': stride_cnmf,
            'method_init': method_init,
            'rolling_sum': True,
            'only_init': True,
            'ssub': ssub,
            'tsub': tsub,
            'merge_thr': merge_thr, 
            'min_SNR': min_SNR,
            'rval_thr': rval_thr,
            'use_cnn': True,
            'min_cnn_thr': cnn_thr,
            'cnn_lowest': cnn_lowest}
    
    brennaParams20x = {
    'fnames': fnames,
                'fr': 31,
                'decay_time': 0.3,
                'p': 0,
                'nb': 2,
                'rf': 24,
                'K': 4, 
                'gSig': [4,4],
                'stride': 8,
                'method_init': 'greedy_roi',
                'rolling_sum': True,
                'only_init': True,
                'ssub': 2,
                'tsub': 2,
                'merge_thr': 0.60, 
                'min_SNR': 2.0,
                'rval_thr': 0.80,
                'use_cnn': True,
                'min_cnn_thr': 0.90,
                'cnn_lowest': 0.30}
    

    brennaParams40x = {
        'fnames': fnames,
                'fr': 31,
                'decay_time': 0.3,
                'p': 2,
                'nb': 2,
                'rf': 45,
                'K': 6, 
                'gSig': [7,7],
                'stride': 20,
                'method_init': 'greedy_roi',
                'rolling_sum': True,
                'only_init': True,
                'ssub': 2,
                'tsub': 2,
                'merge_thr': 0.60, 
                'min_SNR': 2.0,
                'rval_thr': 0.80,
                'use_cnn': True,
                'min_cnn_thr': 0.90,
                'cnn_lowest': 0.30}
    

    GabiParams20x = {
        'fnames': fnames,
                'fr': 31,
                'decay_time': 0.3,
                'p': 2,
                'nb': 2,
                'rf': 24,
                'K': 6, 
                'gSig': [4,4],
                'stride': 14,
                'method_init': 'greedy_roi',
                'rolling_sum': True,
                'only_init': True,
                'ssub': 1,
                'tsub': 2,
                'merge_thr': 0.80, 
                'min_SNR': 2.0,
                'rval_thr': 0.80,
                'use_cnn': True,
                'min_cnn_thr': 0.90,
                'cnn_lowest': 0.30}
    

    GabiParams40x = {
        'fnames': fnames,
                'fr': 31,
                'decay_time': 0.3,
                'p': 2,
                'nb': 2,
                'rf': 45,
                'K': 4, 
                'gSig': [7,7],
                'stride': 20,
                'method_init': 'greedy_roi',
                'rolling_sum': True,
                'only_init': True,
                'ssub': 2,
                'tsub': 2,
                'merge_thr': 0.60, 
                'min_SNR': 2.0,
                'rval_thr': 0.80,
                'use_cnn': True,
                'min_cnn_thr': 0.90,
                'cnn_lowest': 0.30}
    

    gabiParams = {'gabi20x': GabiParams20x, 'gabi40x': GabiParams40x}
    brennaParams = {'brenna20x': brennaParams20x, 'brenna40x': brennaParams40x}

    params = {'gabi': gabiParams, 'brenna':brennaParams}
    if userSelect == True:
        if "brenna" in paramType.lower():
            userDict = params['brenna']
            if '20' in paramType.lower():
                if userInput == True:
                    tempDict = userDict['brenna20x']
                    for pName in Optionalparams.keys():
                        if pName in defaultDict:
                            tempDict[pName] = Optionalparams[pName]
                            paramsDict = tempDict
                else:
                    paramsDict = userDict['brenna20x']
            elif '40' in paramType.lower():
                paramsDict = userDict['brenna40x']
                if userInput == True:
                    tempDict = userDict['brenna40x']
                    for pName in Optionalparams.keys():
                        if pName in defaultDict:
                            tempDict[pName] = Optionalparams[pName]
                            paramsDict = tempDict
                else:
                    paramsDict = userDict['brenna40x']
            else:
                raise Exception("No parameters found with the given inputs. Please try another name, or enter your own parameters dictionary")
        elif "gabi" in paramType.lower():
            userDict = params['gabi']
            if '20' in paramType.lower():
                if userInput == True:
                    tempDict = userDict['gabi20x']
                    for pName in Optionalparams.keys():
                        if pName in defaultDict:
                            tempDict[pName] = Optionalparams[pName]
                            paramsDict = tempDict
                else:
                    paramsDict = userDict['gabi20x']
            elif '40' in paramType.lower():
                paramsDict = userDict['gabi40x']
                if userInput == True:
                        tempDict = userDict['gabi40x']
                        for pName in Optionalparams.keys():
                            if pName in defaultDict:
                                tempDict[pName] = Optionalparams[pName]
                                paramsDict = tempDict
                else:
                    paramsDict = userDict['gabi40x']
            else:
                raise Exception("No parameters found with the given inputs. Please try another name, or enter your own parameters dictionary")
        else:
            raise Exception("No parameters found with the given inputs. Please try another name, or enter your own parameters dictionary")
    elif userSelect == False:
        if userInput == False:
            paramsDict = defaultDict
        else:
            for pName in Optionalparams.keys():
                if pName in defaultDict:
                    defaultDict[pName] = Optionalparams[pName]
            paramsDict = defaultDict
    else:
       raise Exception("No parameters found with the given inputs. Please try another name, or enter your own parameters dictionary") 
    return paramsDict