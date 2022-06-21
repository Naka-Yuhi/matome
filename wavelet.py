import py_module.negenovation as ngi
import numpy as np
import os
import matplotlib.pyplot as plt
import sys,time

par_dir = os.path.abspath(os.path.join( os.pardir ))
data_list = ngi.readNPY(par_dir)
_, length,_ = ngi.readtxt(par_dir)

####### Wavelet transform ##################
import pywt
import gc
import sys

sys_args = sys.argv


if len(sys_args) == 2:
    if not ( sys_args[1] == 'power' or sys_args[1] == 'log'):
        raise ValueError("the second argument must be 'power' or 'log'.")
        sys.exit()
    result_type = sys_args[1]
    wavelet_type = 'cmor1.5-1.0'

elif len(sys_args) == 3:
    if not ( sys_args[1] == 'power' or sys_args[1] == 'log'):
        raise ValueError("the second argument must be 'power' or 'log'.")
        sys.exit()
    try:
        B_value = float(sys_args[2])
    except ValueError as e:
        print(e)
        sys.exit()
    
    result_type = sys_args[1]
    wavelet_type = 'cmor' + str(B_value) + '-1.0'
else:
    result_type = 'power'
    wavelet_type = 'cmor1.5-1.0'





if result_type == 'log':
    dir = './image/wavelet/accomp_len/' + result_type + '/' + wavelet_type
    lim_max = [6,5,3]
    lim_min = [-6,-6,-6]
elif result_type == 'power':
    dir = './image/wavelet/accomp_len/' + result_type + '/' + wavelet_type
    lim_max = [5,4,2]
    lim_min = [0,0,0]

if not os.path.isdir(dir):
    os.makedirs(dir)
    
time_const = 60




for i,data in enumerate(data_list,1):

    if i > len(data_list)-1:
        break
    data = data[200:-100,:]

    sys.stdout.write("%d / %d\n" % (i,len(data_list)-1))
    sys.stdout.flush()

    fig = plt.figure(0,figsize=(14,8),dpi=90)
    ax = fig.add_subplot(2,3,(1,3))
    
    ############  to display lenght  #####################
    ax.plot(length[:,0],length[:,2],color='b',zorder=0.1)
    ax.scatter(length[i,0],length[i,2],color='r',zorder=1,s=25)
    ax.set_xlabel("Time $t$ [h]",fontsize=14)
    ax.set_ylabel("Variations of tool length [$μm$]",fontsize=14)
    ax.set_ylim(-80,10)
    ax.set_xlim(0,5)
    ######################################################
    
    t = np.arange(data.shape[0])*1/80000
    


    scale = np.arange(8,200)
    dirtitle = ["X","Y","Z"]

    increas_per = 100/3
    progress_per = 0
    
    for j in range(3):
        progress_per += increas_per
        
        each_data = data[:,j]
        coef,freq = pywt.cwt(each_data,scales=scale,wavelet=wavelet_type,method='fft',sampling_period=1/80000)
        
        if result_type == 'log':
            coef = 10*np.log10( np.abs(coef[:,0:-1:8]) )
        elif result_type == 'power':
            coef = np.abs(coef[:,0:-1:8])
            
        ax = fig.add_subplot(2,3,j+4)    
        mapper = ax.pcolormesh(t[0:-1:8],freq,coef,cmap='jet',vmin=lim_min[j],vmax=lim_max[j])
        
        #mapper = ar[counter].pcolormesh(t,freq,np.abs(coef),cmap='jet')
        ax.set_yscale('log')
        ax.set_ylabel("Frequency $f$ [$Hz$]",fontsize=14)
        ax.set_xlabel("Time $t$ [$s$]",fontsize=14)
        ax.set_title(dirtitle[j],fontsize=20)

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
            fig.savefig(dir +  '/' + str(round(length[i,0]*time_const,1))  + "min.png")

            sys.stdout.write("\033[2K\033[21D%s\n" % (progress))
            sys.stdout.flush()

            plt.clf()
            


    