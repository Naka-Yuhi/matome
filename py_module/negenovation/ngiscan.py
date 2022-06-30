import os
import glob
import pickle
import numpy as np
import copy
from natsort import natsorted
from tqdm.notebook import trange
import gc
import yaml
import datetime
import traceback
import sys


def readtxt(path,fileform='data',time_span=9.7):
	""" ==  readtxt  ==========
	
	"""

	folders = __findpath(path,fileform,'txt')

	if len(folders) == 0:
		return (None,None,None)

	#the variable of path replesent the parent's path
	
	length = []
	time_len = []
	all_datas = np.zeros((100000,8))
	counter_base = 0

	fig_title = ["0h"]
		
	for data_folder in folders:
		files_txt = natsorted(glob.glob(  os.path.join( data_folder, fileform + "*" + '.txt')   ))

		#print("---------------------------")
		#print(data_folder)
		for i,file_name in enumerate(files_txt):
			
			f = open(file_name,'r',encoding="utf-8")
			f.readline()[:-1]
			length.append( int( f.readline()[:-1] )/10000 )
			f.close()

			data_np = np.loadtxt(file_name,delimiter=',',skiprows=2)

			#print(np.mean(data_np,axis=0))
			#the first tool length is decided to be 0
			
			time_len.append( (counter_base*time_span) )
			all_datas[counter_base,1:8] = np.mean(data_np,axis=0)
			all_datas[counter_base,0] = ( ((counter_base+1)*time_span) - time_span/2 )/60 
			
			counter_base += 1

		fig_title.append( str( round(time_len[-1]/60,1) ) + "h" )
	
	logi = all_datas[:,3] != 0
	
	new_length = np.vstack([np.array(time_len), np.array(length),np.array(length) - np.array(length)[0]]).T
	new_length[:,2] *= 1000
	
	return (all_datas[logi,:], new_length, fig_title)

def readtxt2(path,fileform='data',data_offset=5,return_type='each'):
	""" ==  readtxt  ==========
	
	"""
	########################################################
	folders = __findpath(path,fileform,'txt')
	########################################################

	if len(folders) == 0:
		return (None,None,None)

	#the variable of path replesent the parent's path
	
	length = []
	time_len = []

	start_end_index = []
	
	
	indx_start = 0
	indx_end = 0
	counter_base = 0
	
	fig_title = ["0h"]
	new_all_data = []
	print(fig_title[-1],end="->")

	for data_folder in folders:
		
		files_txt = natsorted(glob.glob(  os.path.join( data_folder, fileform + "*" + '.txt')   ))
		# reading all the files
		#length : tool length
		#time_len : time for tool length
		#data_np
		
		
		#print("---------------------------")
		#print(data_folder)
		for i,file in enumerate(files_txt):
		
			
			f = open(file,'r',encoding="utf-8")
			f.readline()[:-1]
			length.append( int( f.readline()[:-1] )/10000 )
			f.close()
			data_np = np.loadtxt(file,delimiter=',',skiprows=2)
			
			indx_end += data_np.shape[0]

			start_end_index.append([indx_start,indx_end])

			time = np.arange(indx_start,indx_end)*0.25/3600


			if counter_base == 0:
				time_len.append(0)
			else:
				#indx_start,indx_endを使用して時間を作成した場合、ずれが生じるため
				#The time was newly defined for tool length.
				time_len_arr = np.arange( start_end_index[counter_base-1][0],start_end_index[counter_base-1][1] )*0.25/3600
				time_len.append(time_len_arr[-1])
			


			##applying offset
			time = time[data_offset-1:-data_offset]
			data_np = data_np[data_offset-1:-data_offset]
			data = np.hstack( (time.reshape(time.shape[0],1) ,data_np) )

			##add data into new_all_data
			new_all_data.append( data )
			if counter_base == 0:
				data_combined = data
			else:
				data_combined = np.vstack(  (data_combined,data) )
			counter_base += 1

			indx_start = indx_end
		
		fig_title.append( str( round(time_len[-1],1) ) + "h" )
		print(fig_title[-1],end="->")
	print("END")
	
	
	new_length = np.vstack([np.array(time_len), np.array(length),np.array(length) - np.array(length)[0]]).T
	new_length[:,2] *= 1000


	if return_type == 'each':
		return (new_all_data, new_length, fig_title)	
	if return_type == 'combine':
		return (data_combined,new_length,fig_title)
	else:
		return( None, new_length, fig_title)
	
def readNPY( path,fileform='data'):
	""" ==  readNPY  ==========
	
	"""
	data_list = []

	folders = __findpath(path,fileform,'npy')
	if len(folders) == 0:
		return data_list

	for data_folder in folders:
		files_txt = natsorted(glob.glob(  os.path.join( data_folder, '*npy')   ))
		
		# reading all the files
		#length : tool length
		#time_len : time for tool length
		#data_np
		
		
		#print("---------------------------")
		#print(data_folder)
		for i,file in enumerate(files_txt):
			data = np.load(file)
			data_list.append( __sortdata(data) )
				
	
	return data_list

def readCSV(path,fileform='data'):
	""" ==  readNPY  ==========
	
	"""
	data_list = []

	folders = __findpath(path,fileform,'csv')
	if len(folders) == 0:
		return data_list


	for i in trange(len(folders)):
		file_counter = 0
		data_folder = folders[i]
		files_csv = natsorted(glob.glob(  os.path.join( data_folder, fileform + '*csv')   ))
		
		# reading all the files
		#length : tool length
		#time_len : time for tool length
		#data_np
		
		
		#print("---------------------------")
		#print(data_folder)
		for i in trange(len(files_csv),leave=False):
			file_csv = files_csv[i]
			data = np.loadtxt(file_csv,delimiter=",",dtype=np.float32)
			sorted_data = __sortdata(data)
			
			np.save( os.path.join(data_folder,fileform + "_" + str(file_counter) + ".npy") ,sorted_data )
			data_list.append( sorted_data )
			file_counter += 1

			del data,sorted_data
			gc.collect()
				
	
	return data_list

def readyaml(path,work_name="e.max",readfunc='readtxt'):
	'''

	
	'''
	#latest yaml information
	up_to_date = True

	if os.path.isfile( path ):
		file_yml = path
	else:
		files_yml = natsorted(glob.glob(os.path.join(path,'*.yml') ) )
		if len(files_yml) == 0:
			try:
				raise FileNotFoundError("yaml file was not found.")
			except:
				traceback.print_exc()
				return
		else:
			file_yml = files_yml[0]

	with open(file_yml,'r') as yml:
		config = yaml.safe_load(yml)

	#print(config)

	#calculation of machining time
	parpath = os.path.abspath( os.path.join( os.pardir ))
	if readfunc == 'readtxt':
		_, length,_ = readtxt(parpath)
	elif readfunc == 'readtxt2':
		_, length,_ = readtxt2(parpath)

	#a type of machining_time variable is numpy.numpy, so machining_time has to be changed into float.
	machining_time = round(  float(length[-1,0]) ,2 )
	
	
	#In case of Mechining time filled with empty or not equal to machining time calculated above
	if config['condition']['machining_time'] is None:
		config['condition']['machining_time'] = machining_time
		up_to_date = False
		#print("ok1")
	elif config['condition']['machining_time'] != machining_time:
		config['condition']['machining_time'] = machining_time
		up_to_date = False
		#print("ok2")

	#comment is empty
	if config['condition']['description'] is None:
		config_comment = "no comment"
	else:
		config_comment = config['condition']['description']

	start_time = config['condition']['date']['start'].strftime('%Y/%m/%d (%a)')
	end_time = config['condition']['date']['end'].strftime('%Y/%m/%d (%a)')
	
	# work type is not defined
	work_info_path = os.path.join(os.getcwd(),"py_module","workpiece_info",work_name+".yml")
	if not os.path.isfile(work_info_path):
		raise FileNotFoundError("work_name might be wrong word.")
		sys.exit()
	with open(work_info_path,'r',encoding='utf-8') as yml:
			work_info = yaml.safe_load(yml)

	
	if not 'workpiece' in config:
		up_to_date = False
		config['workpiece'] = work_info
	
	
	####### DISPLAY  ################
	print(config['condition']['Nnumber'])
	print("==========  Condition  ===============")
	print('加工開始日：' + start_time)
	print('加工終了日：' + end_time)
	print('回転数：' + str( config['condition']['rotation_speed'] ) + "rpm")
	print('送り速度：' + str(config['condition']['feedrate'] ) + 'mm/min')
	print('切り込み幅：' + str( config['condition']['ae']) + 'mm')
	print('切り込み深さ：' + str(config['condition']['ap']) + 'mm')
	print('加工時間：' + str( config['condition']['machining_time'] ) + 'h')
	print('加工のパターン：' + config['condition']['process_type'])
	print('コメント：' + config_comment)
	print("==========  Workpiece  ===============")
	print('製品名 : ' + config['workpiece']['product_name'])
	print('材料の種類 : ' + config['workpiece']['type'])
	print('構成材料 : ' + str(config['workpiece']['constituent_material']))
	
	#if yaml file is not up_to_date, the following code will be carryed out
	if not up_to_date:
		#print("ok3")
		with open(file_yml,'w') as yml:
			yaml.dump(config,yml,encoding='utf-8', allow_unicode=True)
	return config

#####################################################
#				Private functions					#
#####################################################
def __sortdata(data):
	indx_sort = [0,0,0]
	#print(data.shape)
	data_mean = np.mean(data,axis=0)
	z_posi = np.argmin(data_mean)

	
	for j in [2,0,1]:
		indx_sort[j] = int(z_posi)
		
		if z_posi == 2:
			z_posi = 0
		else:
			z_posi += 1

	return data[:,indx_sort]


def __findpath(path,fileform,filetype):
	
	folders = []
	file_ext = fileform + '*' + filetype

	#親フォルダ下のフォルダのパスを格納する。
	folder_lv1 = natsorted(glob.glob(  os.path.join( path, '[0-9-h.]*')   ))

	for each_folder_lv1 in folder_lv1:
		files_txt = natsorted(glob.glob(  os.path.join( each_folder_lv1,file_ext)   ))

		if len(files_txt) != 0:
			folders.append(each_folder_lv1)
			#print(each_folder_lv1)
			#print(files_txt)
		else:
			#さらに下の階層を読み込む
			folder_lv2 = natsorted(glob.glob(  os.path.join( each_folder_lv1, '[0-9-h.]*')   ))

			#level2のフォルダないのコンテンツを読み込む
			for each_folder_lv2 in folder_lv2:
				files_txt = natsorted(glob.glob(  os.path.join( each_folder_lv2,file_ext)   ))

				if len(files_txt) != 0:
					folders.append(each_folder_lv2)
					#print(each_folder_lv2)
					#print(files_txt)

	return folders