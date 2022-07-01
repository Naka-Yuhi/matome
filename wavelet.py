import py_module.negenovation as ngi
import numpy as np
import matplotlib.pyplot as plt
import sys,yaml,gc,pywt,os,re
import traceback

def main():
    ####### Wavelet transform ##################

    wavelet_list = readMotherWavelets("./py_module/mother_wavelets/mother_wavelets.yml")

    sys_args = sys.argv

    result_type = 'power'
    wavelet_type = 'cmor1.5-1.0'
    panel_type = 'H'

    for i,sys_arg in enumerate(sys_args,0):
        if i == 0:
            continue
        elif i == 1:
            if not( "mother_wavelet" in sys_arg or  sys_arg == "--help" ):
                ValueError("first option must be 'mother_wavelet' or '--help'")
                sys.exit()
        
        if not "=" in sys_arg:
            print("Error : a option is wrong format.")
            sys.exit()
        
        option = sys_arg.split("=")


        if option[0] == 'mother_wavelet':
            if option[1] in wavelet_list.keys():
                wavelet_type = option[1]
                requirement_num = wavelet_list[option[1]]['requirement']
                output_of_wavelet = wavelet_list[option[1]]['result']
                print("MV: %s, Req_num: %d, Result: %s" % (wavelet_type,requirement_num,output_of_wavelet))
            else:
                print("Error : mother_wavelet called %s could not be found." % option[1])
                sys.exit()
        elif option[0] == 'cons_val':

            cons_value = option[1].replace('[','').replace(']','').split(',')

            if requirement_num == 0:
                print('Warning : cons_val option is not required')
                sys.exit()
            elif len(cons_value) < requirement_num:
                print("Error : parameter is missing: the number of required arguments = %d" % requirement_num)
                sys.exit()
            elif len(cons_value) > requirement_num:
                print("Error : too much arguments")
                sys.exit()

            try:
                for val in cons_value:
                    val_float = float(val)
                    wavelet_type += str(val_float) + "-"
                
                wavelet_type = wavelet_type[:-1]
            except ValueError as e:
                print(traceback.format_exc())
                sys.exit()
        elif option[0] == 'panel_type':
            pattern_v = re.compile(r'v|V|vertical|vert')
            pattern_h = re.compile(r'h|H|horizonal|horz')

            if bool(pattern_v.match(option[1])):
                panel_type = 'V'
            elif bool(pattern_h.match(option[1])):
                panel_type = 'H'
        elif option[0] == 'result_type':
            if option[1] == 'power':
                result_type = 'power'
            elif option[1] == 'log':
                result_type = 'log'
            else:
                print("Error : result_type option is wrong word.")
                sys.exit()
            
        else:
            print("Error : unknown option")
            sys.exit()

    par_dir = os.path.abspath(os.path.join( os.pardir ))
    data_list = ngi.readNPY(par_dir)
    _, length,_ = ngi.readtxt2(par_dir)

    print("-----------------------------------")
    print("~~~~~  Machining Conditions  ~~~~~~~~")
    ngi.readyaml(par_dir,readfunc='readtxt2')


    print("~~~~~  Wavelet Transform Part  ~~~~~~~~")
    print("Output Type    : %s" % result_type)
    print("Mother Wavelet: %s" % wavelet_type)
    print("-----------------------------------")

    if result_type == 'log':
        dir = './image/wavelet/accomp_len/' + result_type + '/' + wavelet_type + "-" + panel_type
        lim_max = [9,5,5]
        lim_min = [-6,-6,-6]
    elif result_type == 'power':
        dir = './image/wavelet/accomp_len/' + result_type + '/' + wavelet_type + "-" + panel_type
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

        if panel_type == 'V':
            fig = plt.figure(0,figsize=(14,16),dpi=90)
            ax = fig.add_subplot(4,1,1)

        elif panel_type == 'H':
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

            if panel_type == 'V':
                ax = fig.add_subplot(4,1,2+j)

            elif panel_type == 'H':  
                ax = fig.add_subplot(2,3,j+4)

            #mapper = ax.pcolormesh(t[0:-1:8],freq,coef,cmap='jet',vmin=lim_min[j],vmax=lim_max[j])
            
            mapper = ax.pcolormesh(t[0:-1:8],freq,coef,cmap='jet')
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


def readMotherWavelets(file_path):
    with open(file_path,'r') as yml:
        return yaml.safe_load(yml)


if __name__ == "__main__":
    main()
            


    