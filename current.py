import py_module.negenovation as ngi
import numpy as np
import os
import matplotlib.pyplot as plt
import sys,time
import re


sys_args = sys.argv
print(sys_args)

axis1_max = 2000
axis1_min = 1300

axis2_max = 1800
axis2_min = 1550
axix_time = "h"


p = re.compile(r'\[[0-9.]+,[0-9.]+\]')

for i,arg in enumerate(sys_args):
    #the first argument is file name, so it will not be adoptted.
    if i==0:
        continue

    if not "=" in arg:
        raise ValueError("the option format must be 'key'='value'.")
        sys.exit()
    
    option = arg.split('=')
    

    if option[0] == "type":
        type_ver = int( option[1] )


    elif option[0] == "axis1":
        m = p.match(option[1])
        if m == None:
            raise ValueError("Options are unsuported format")
            sys.exit()
            
        splited_values = re.split('[\[\],]',m.group())
        
        try:
            axis1_min = float(splited_values[1])
            axis1_max = float(splited_values[2])
        except TypeError as e:
            print("TypeError: cannot convert the original value into float")
            sys.exit()
        
    elif option[0] == "axis2":
        m = p.match(option[1])
        if m == None:
            raise ValueError("Options are unsuported format")
            sys.exit()
            
        splited_values = re.split('[\[\],]',m.group())
        
        try:
            axis2_min = float(splited_values[1])
            axis2_max = float(splited_values[2])
        except TypeError as e:
            print("TypeError: cannot convert the original value into float")
            sys.exit()
    else:
        raise ValueError("Options are unsuported format.")
        sys.exit()
    
    
    




par_dir = os.path.abspath(os.path.join( os.pardir ))
all_data, length,fig_title = ngi.readtxt(par_dir)

#print(all_data)

fig = plt.figure(0,figsize=(10,4),dpi=150)
ax = fig.subplots(1,1)

print(len(all_data))
sp_means = []

type_ver = 0


if not os.path.isdir("./image/current/"):
    os.makedirs("./image/current/")



if type_ver == 0:
    ax.plot(all_data[:,0],all_data[:,7])
    ax.set_xlabel("Time $t$ [h]",fontsize=18)
    ax.set_ylabel("SP current",fontsize=18)
    ax.set_ylim(axis1_min,axis1_max)
    ax.set_xlim(0,all_data[-1,0])

else:
    for each_data in all_data:
        
        data = each_data[:,:]
        size_data = data.shape[0]
        sp_mean = np.mean(data[:,7],axis=0)

        line1, = ax.plot(data[:,0],data[:,7],color='b',zorder=0)
        
        
        sp_means.append([data[size_data//2,0],sp_mean])




    sp_means = np.array(sp_means)

    ax2 = ax.twinx()
    line2, = ax2.plot(sp_means[:,0],sp_means[:,1],'.r-',zorder=0.5)

    for i,change_time_str in enumerate(fig_title):
        if i == 0 or i == len(fig_title)-1:
            continue

        change_time_str = change_time_str.split("h")
        change_time = float(change_time_str[0])
        
        line3, = ax.plot([change_time,change_time],[axis1_min,axis1_max],'c--',zorder=1)




    ax2.set_ylabel("Average SP current",fontsize=18)
    ax2.set_ylim(axis2_min,axis2_max)

    ax.set_xlabel("Time $t$ [h]",fontsize=18)
    ax.set_ylabel("SP current",fontsize=18)
    ax.set_ylim(axis1_min,axis1_max)
    ax.set_xlim(0,each_data[-1,0])

    if "line3" in locals():
        ax.legend([line1,line2,line3],["SP current", "Average SP current","The point exchanging a workpiece"])
    else:
        ax.legend([line1,line2],["SP current","Average SP current"])




fig.tight_layout()
fig.savefig("./image/current/current.png")


plt.show()