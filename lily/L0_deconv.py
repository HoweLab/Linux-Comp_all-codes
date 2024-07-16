#%%
import numpy as np
import pandas as pd
import os, time, sys, warnings
#import pickle5 as pickle
import pickle

import scipy.io 
#sys.path.append('/Users/hadenpelletier/opt/anaconda3/lib/python3.8/site-packages/')

from FastLZeroSpikeInference import fast
from L0_analysis import L0_analysis

#%%
def fit_lambda(dffs,event_min_size = 5):
    l0a = L0_analysis(dffs, event_min_size = event_min_size, 
                      use_cache=False)
    l0a.dff_traces
    l0a.L0_constrain=True # only zero or positive events
    l0a.get_events(use_bisection=True)
    return l0a
#%%
def run_l0events(l0,dffs):
    est_all=[]
    times_all=[]
    events_all=[]
    for ii,dff in enumerate(dffs):
        lam = l0.lambdas[ii]
        gamma = l0.gamma
        y = dffs[ii]
        fit = fast.estimate_spikes(y, gamma, lam, False, True)

        times =  fit['spikes'] #event frames
        events = fit['pos_spike_mag'] #this still returns zt=0 as possible event size.

        if 0 in events:
            zero_ind = np.argwhere(events == 0).flatten()
            times = np.delete(times,zero_ind)
        events = events[events!= 0]

        est_all.append(fit['estimated_calcium'])
        times_all.append(times)
        events_all.append(events)

    dec={
        'dff': dffs,
        'est': np.asarray(est_all),
        'times': times_all,
        'events': events_all,
        'gamma': l0.gamma,
        'lambda': l0.lambdas,
    }
    return dec

# #%%
# def deconvolve(file,path):

#     fname = os.path.split(file)[-1].split('.')[0]
#     dffs = np.load(file,allow_pickle=True)['dff']

#     l0 = fit_lambda(dffs)
#     dec = run_l0events(l0,dffs)

#     with open(os.path.join(path,fname+'_l0analysis.pkl'),'wb') as file:
#         pickle.dump(l0,file,protocol=pickle.HIGHEST_PROTOCOL)
#     with open(os.path.join(path,fname+'_l0deconv.pkl'),'wb') as file2:
#             pickle.dump(dec,file2,protocol=pickle.HIGHEST_PROTOCOL)
# #%%
# def main():
#     path='/projectnb/engram/deconvolution/deconv_results'
#     deconvolve(sys.argv[1],path)

def main():
    mat = scipy.io.loadmat('SampleData_Old.mat')
    df = pd.DataFrame(mat['Fc'])
    # Cells 1-2
    df_test = df[[1,2,3]].T
    y = np.array(df_test) # (n,t) array n#traces, t#frames
    l0 = fit_lambda(y)
    dec = run_l0events(l0,y)

    #path='deconvolution/deconv_results'

    with open('l0deconv.pkl','wb') as file:
        pickle.dump(dec,file,protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    main()


