from FastLZeroSpikeInference import fast
import numpy as np


gam  = 0.98
y = np.power(gam,np.concatenate([np.arange(100),np.arange(100)]))

fit = fast.estimate_spikes(y,gam,1, False)

print(fit)