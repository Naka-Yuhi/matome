import py_module.negenovation as ngi
import numpy as np
import os
import matplotlib.pyplot as plt
import sys,time
import 


par_dir = os.path.abspath(os.path.join( os.pardir ))
data_list = ngi.readNPY(par_dir)
_, length,_ = ngi.readtxt(par_dir)

####### Wavelet transform ##################
import pywt
import gc
from tqdm.notebook import trange



if not os.path.isdir('./image/wavelet/accomp_len/min'):
    os.makedirs('./image/wavelet/accomp_len/min')
    
time_const = 60


lim_val = [5,4,2]

for i,data in enumerate(data_list,1):
    data = data[200:-100,:]

    sys.stdout.write("%d / %d\n" % (i,len(data_list)-1))
    sys.stdout.flush()

    fig = plt.figure(0,figsize=(14,8),dpi=90)
    ax = fig.add_subplot(2,3,(1,3))
    
    ############  to display lenght  #####################
    ax.plot(length[:,0],length[:,2],color='b',zorder=0.1)
    ax.scatter(length[i,0],length[i,2],color='r',zorder=1,s=25)
    ax.set_xlabel("Time t[h]",fontsize=16)
    ax.set_ylabel("Variations of tool length [μm]",fontsize=16)
    ax.set_xlim(0,5)
    ######################################################
    
    t = np.arange(data.shape[0])*1/80000
    wavelet_type = 'cmor1.5-1.0'


    scale = np.arange(8,200)
    dirtitle = ["X","Y","Z"]

    increas_per = 100/3
    progress_per = 0

    
    
    if i == 1:
        prev_coef_list = []
        for j in range(3):
            each_data = data[:,j]
            prev_coef_list.append(pywt.cwt(each_data,scales=scale,wavelet=wavelet_type,method='fft',sampling_period=1/80000))
            print("ok")
    else:
        for j in range(3):
            progress_per += increas_per
            
            each_data = data[:,j]
            coef,freq = pywt.cwt(each_data,scales=scale,wavelet=wavelet_type,method='fft',sampling_period=1/80000)
            
            ax = fig.add_subplot(2,3,j+4)
            mapper = ax.pcolormesh(t[0:-1:8],freq,np.abs(coef[:,0:-1:8]),cmap='jet',vmin=0,vmax=lim_val[j])
            #mapper = ar[counter].pcolormesh(t,freq,np.abs(coef),cmap='jet')
            ax.set_yscale('log')
            ax.set_ylabel("Frequency f[Hz]",fontsize=16)
            ax.set_xlabel("Time t[s]",fontsize=16)
            ax.set_title(dirtitle[j],fontsize=18)

            pp = fig.colorbar(mapper,ax=ax, orientation="vertical")
            del coef,freq
            gc.collect()
            progress = "===="*(j+1)
            progress = progress + "    "*(2-j) + "> : " + str( round(progress_per,1) ) + "%"
            if j == 0:
                sys.stdout.write("\033[2K\033[" + str(len(progress)) + "D%s" % (progress))
                sys.stdout.flush()
            if j==1:
                sys.stdout.write("\033[2K\033[" + str(len(progress)) + "D%s" % (progress))
                sys.stdout.flush()
            if j==2:

                fig.tight_layout()
                fig.savefig("./image/wavelet/accomp_len/min/" + str(round(length[i,0]*time_const,1))  + "min.png")

                sys.stdout.write("\033[2K\033[21D%s\n" % (progress))
                sys.stdout.flush()

                plt.clf()
            


    