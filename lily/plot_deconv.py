import numpy as np
#import holoviews as hv
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import pickle

def ev_trace(events,times,T):
    '''
    convert event magnitudes and times into deconvolved activity traces
    events: array, (N,) N number of neurons, events[i] are the event magnitudes for ith neuron
    times: array, (N,), N number of neurons, times[i] are the frame timestamps for each event
    T: total number of frames (size of df)
    returns: ev, NxT array of deconvolved activity
    '''
    N = events.shape[0]
    ev = np.zeros([N,T])

    for i in np.arange(0,N):
        event_cell=events[i]
        times_cell = times[i]
        ev[i,times_cell]=event_cell
    return ev

def plot_deconv(dff, est, events, times, i, frame_rate=30):
    '''
    dff: dF/F NxT array
    est: deconvolution model fit NxT array
    events: event magnitudes, array of size N
    times: event frames/times, array of size N
    i: cell index
    T: length of timeseries (frames)
    frame_rate: default 30
    returns: holoview overlay of traces for single cell, for jupyter interactive notebook
    '''
    dff = dff[i, :]
    est = est[i, :]
    ev = events[i]
    times = times[i]

    # d = np.zeros(T)
    # d[times] = ev

    event_plot = times, -2 * np.ones(times.shape)
    #t = T / frame_rate
    plt.eventplot(event_plot,zorder=5,color='red')
    plt.plot(dff+2, label='Calcium', color='blue')
    fig = plt.gcf()
    ax = plt.gca()
    ax.set_position([0.15,0.25,0.8,0.5])
    disp_span = 4000
    ax.set_xlim(0,disp_span)
    def val_change(val):
        ax.set_xlim(val,val+disp_span)
    axsl = fig.add_axes([0.15,0.05,0.8,0.03])
    sl = Slider(axsl, label = "frames", valmin = 0, 
                valmax = dff.shape[0]-3000,
                valinit = 0,
                orientation= 'horizontal')
    sl.on_changed(val_change)
    plt.show()

    # plot = hv.Curve(dff, label='Raw df/f').opts(width=900, height=300, ylabel='df/f', xlabel='Frame #') * \
    #        hv.Curve(est, label='Deconvolution model fit').opts(width=900, height=300, color='#e5ae38') * \
    #        hv.Curve(d, label='Deconvolved activity').opts(width=900, height=300, color='red') * \
    #        hv.Scatter(event_plot, label='Spikes').opts(fill_color='k', line_color='k', size=3)
    # plot.opts(legend_position='right')

    return fig

def main():
    with open('l0deconv.pkl','rb') as file:
        data = pickle.load(file)
        dff = data['dff']
        est = data['est']
        events = data['events']
        times = data['times']
        gamma = data['gamma']
        lambdas = data['lambda']

    plot_deconv(dff,est,events,times,0)

if __name__ == '__main__':
    main()