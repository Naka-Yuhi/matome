import py_module.negenovation as ngi
import numpy as np
import os
import matplotlib.pyplot as plt
import sys,time


sys_args = sys.argv

axis_max = 1800
axis_min = 1550
axix_time = "h"

for i,arg in enumerate(sys_args):
    #the first argument is file name, so it will not be adoptted.
    if i==0:
        continue

    print(arg)
    if not "=" in arg:
        raise ValueError("the option format must be 'key'='value'.")
        sys.exit()
    
    option = arg.split('=')
    
    
    if option[0] == 'max':
        try:
            value = float(option[1])
        except ValueError as e:
            print("value must be the number")
            sys.exit()
        axis_max = value
    elif option[0] == 'min':
        try:
            value = float(option[1])
        except ValueError as e:
            print("value must be the number")
            sys.exit()
        axis_min = value
    elif option[0] == 'time':
        value = option[1]
        if not ( value == 'h' or value == 'min'):
            raise ValueError("the value in option of time must be h or min.")
            sys.exit()
    else:
        raise ValueError("the option must be min,max,time")
        sys.exit()




par_dir = os.path.abspath(os.path.join( os.pardir ))
all_data, length,_ = ngi.readtxt2(par_dir,data_offset=10)

fig = plt.figure(0,figsize=(10,4),dpi=150)
ax = fig.subplots(1,1)

print(len(all_data))
sp_means = []



if not os.path.isdir("./image/current/"):
    os.makedirs("./image/current/")

for each_data in all_data:
    
    data = each_data[:-5,:]
    size_data = data.shape[0]
    sp_mean = np.mean(data[:,7],axis=0)

    line1, = ax.plot(data[:,0],data[:,7],color='b',zorder=0)
    
    
    sp_means.append([data[size_data//2,0],sp_mean])



sp_means = np.array(sp_means)

ax2 = ax.twinx()
line2, = ax2.plot(sp_means[:,0],sp_means[:,1],'.r-',zorder=1)
ax2.set_ylabel("Average SP current",fontsize=18)
ax2.set_ylim(axis_min,axis_max)

ax.set_xlabel("Time $t$ [h]",fontsize=18)
ax.set_ylabel("SP current",fontsize=18)
ax.set_ylim(1400,2000)
ax.set_xlim(0,each_data[-1,0])

ax.legend([line1,line2],["SP current", "Average SP current"])





fig.tight_layout()
fig.savefig("./image/current/current.png")


plt.show()