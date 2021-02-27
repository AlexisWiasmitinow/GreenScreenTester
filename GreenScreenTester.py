import numpy as np
import cv2
import time, os, operator
from matplotlib import pyplot as plt
from threading import Thread
from GUI import *
from functions import *



t_gui=Thread(target=guiThread)
t_gui.daemon=True
t_gui.start()

now=round(time.time(),0)
i=0
runLoop = True
conversionStartItem=-1
#for i in range(1,100):
while(guiCommands['runLoop']):
	imageFolder=guiCommands['imageFolder']+'/'
	fileList=getFileList(imageFolder)
	#print('length of fileList: ',len(fileList))
	if i<0:
		i=0
	elif i>=len(fileList):
		i=0
	if len(fileList) > 0:
		print('i',i)
		fileName=fileList[i]
		guiCommands['loadedFile']=fileName
		filePath=imageFolder+fileName
		print('loading file: '+filePath)
		inputImage = cv2.imread(filePath)
	else:
		inputImage = None
		i=0
	#cv2.imshow('input',inputImage)
	if inputImage is not None:
		print('loaded file: '+filePath+' i: '+str(i))
		while guiCommands['mode']=='show':
			time.sleep(0.2)
			light_color = (int(guiCommands['hValueL']), int(guiCommands['sValueL']), int(guiCommands['vValueL']))
			dark_color = (int(guiCommands['hValueH']), int(guiCommands['sValueH']), int(guiCommands['vValueH']))
			if guiCommands['useThresh']==0:
				maskedImage, previewImage, alphaImageCropped = computeImagesHSV(inputImage, light_color, dark_color)
			else:
				maskedImage, previewImage, alphaImageCropped = computeImagesThreshold(inputImage, guiCommands['threshLow'], guiCommands['threshUp'])
			show_smaller_image(maskedImage,'HSVmasked '+str(fileName),preview_scale_factor,950,0)
			show_smaller_image(inputImage,'Raw '+str(fileName),preview_scale_factor,1400,0)
			show_smaller_image(previewImage,'alpha Image Cropped '+str(fileName),preview_scale_factor,0,250)
			cv2.waitKey(1)
		
		if guiCommands['mode']=='savePic' or guiCommands['mode']=='convertAll':
			colorString=str(light_color)+str(dark_color)
			colorString=colorString.replace('(','__')
			colorString=colorString.replace(')','__')
			colorString=colorString.replace(',','_')
			saveName='out_'+fileName+'_'+str(colorString)+'.png'
			saveNameAlpha='alpha_'+fileName+'_'+str(colorString)+'.png'
			if guiCommands['mode']=='convertAll':
				if guiCommands['useThresh']==0:
					maskedImage, previewImage, alphaImageCropped = computeImagesHSV(inputImage, light_color, dark_color)
				else:
					maskedImage, previewImage, alphaImageCropped = computeImagesThreshold(inputImage, guiCommands['threshLow'], guiCommands['averageCorrection'])
				cv2.imwrite(imageFolder+saveName,maskedImage)
				cv2.imwrite(imageFolder+saveNameAlpha,alphaImageCropped)
			if guiCommands['mode']=='convertAll':
				if i==conversionStartItem:
					guiCommands['mode']='show'
					conversionStartItem=-1
				else:	
					if conversionStartItem==-1:
						conversionStartItem=i
					i+=1
			else:
				guiCommands['mode']='show'
		elif guiCommands['mode']=='previousPic':
			i-=1
			guiCommands['mode']='show'
		elif guiCommands['mode']=='previousTenPic':
			i-=10
			guiCommands['mode']='show'
		elif guiCommands['mode']=='nextPic':
			i+=1
			guiCommands['mode']='show'
		elif guiCommands['mode']=='nextTenPic':
			i+=10
			guiCommands['mode']='show'
		
		cv2.destroyAllWindows()