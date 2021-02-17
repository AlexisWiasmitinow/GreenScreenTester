import numpy as np
import cv2
import time, os, operator
from matplotlib import pyplot as plt
from threading import Thread
from GUI import *

preview_scale_factor=0.8
font = cv2.FONT_HERSHEY_SIMPLEX


def getFileList(folder):
	fileList={}
	nameList=[]
	try:
		with os.scandir(folder) as allEntries:
			for entry in allEntries:
				if entry.name.endswith('.png') and entry.is_file() and not entry.name.startswith('out_') and not entry.name.startswith('alpha_'):
					#print("allEntries: "+str(entry.name))
					fileList.update([(entry.stat().st_mtime, (entry.name, entry.stat().st_size))])
		sortedList=sorted(fileList.items(),key=operator.itemgetter(0),reverse=True)
		for key,value in sortedList:
			#print(key,value[0])
			nameList.append(value[0])
		return nameList
	except:
		return nameList

def show_smaller_image(image,title,scale,posX,posY):
	dimX , dimY = image.shape[:2]
	out_image=cv2.resize(image,(int(dimY*scale),int(dimX*scale)),interpolation = cv2.INTER_AREA)
	cv2.namedWindow(title)
	cv2.imshow(title,out_image)
	cv2.moveWindow(title,posX,posY)

def computeImages(hsvImage, light_color,dark_color):
	HSVmask = cv2.inRange(hsvImage, light_color, dark_color)
	HSVmaskedImage=cv2.bitwise_and(inputImage,inputImage, mask=HSVmask)
	filledHSVmask = np.zeros((dimX, dimY,1), np.uint8)
	(cntsHSVmask, _) = cv2.findContours(HSVmask, cv2.RETR_EXTERNAL, 2)
	cntsHSVmask = sorted(cntsHSVmask, key = cv2.contourArea, reverse = True)[:1]
	if len(cntsHSVmask) > 0:
		cv2.drawContours(HSVmaskedImage, cntsHSVmask[0], -1, (0, 255, 0), 5)
		box = cv2.boundingRect(cntsHSVmask[0])
		cv2.fillPoly(filledHSVmask,cntsHSVmask,(255,255,255))
		HSVpreviewImage=cv2.bitwise_and(inputImage,inputImage, mask=filledHSVmask)
		cv2.rectangle(HSVmaskedImage,(box[0],box[1]),(box[0]+box[2],box[1]+box[3]),(255,0,0),2)
		testX=280
		testY=400
		alphaImage = cv2.cvtColor(inputImage, cv2.COLOR_BGR2BGRA)
		alphaImage[:,:,3]=filledHSVmask[:,:,0]
		alphaImageCropped=alphaImage[box[1]:box[1]+box[3],box[0]:box[0]+box[2]]
		HSVpreviewImage=HSVpreviewImage[box[1]:box[1]+box[3],box[0]:box[0]+box[2]]
	else:
		print("no contour detected")
	cv2.putText(HSVmaskedImage,str(light_color),(20,40),font,1,(0,255,0), 1,cv2.LINE_AA)
	cv2.putText(HSVmaskedImage,str(dark_color),(20,80),font,1,(0,255,0), 1,cv2.LINE_AA)
	return HSVmaskedImage, HSVpreviewImage, alphaImageCropped

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
		dimX , dimY = inputImage.shape[:2]
		print('loaded file: '+filePath+' i: '+str(i))
		hsvImage =cv2.cvtColor(inputImage,cv2.COLOR_BGR2HSV)
		while guiCommands['mode']=='show':
			time.sleep(0.2)
			cv2.waitKey(1)
			light_color = (int(guiCommands['hValueL']), int(guiCommands['sValueL']), int(guiCommands['vValueL']))
			dark_color = (int(guiCommands['hValueH']), int(guiCommands['sValueH']), int(guiCommands['vValueH']))
			HSVmaskedImage, HSVpreviewImage, alphaImageCropped = computeImages(hsvImage, light_color, dark_color)
			show_smaller_image(HSVmaskedImage,'HSVmasked '+str(fileName),preview_scale_factor,950,0)
			#show_smaller_image(filledHSVmask,'filledHSVmask '+str(fileName),preview_scale_factor)
			show_smaller_image(HSVpreviewImage,'alpha Image Cropped '+str(fileName),preview_scale_factor,0,250)
		
		if guiCommands['mode']=='savePic' or guiCommands['mode']=='convertAll':
			colorString=str(light_color)+str(dark_color)
			colorString=colorString.replace('(','__')
			colorString=colorString.replace(')','__')
			colorString=colorString.replace(',','_')
			saveName='out_'+fileName+'_'+str(colorString)+'.png'
			saveNameAlpha='alpha_'+fileName+'_'+str(colorString)+'.png'
			if guiCommands['mode']=='convertAll':
				HSVmaskedImage, HSVpreviewImage, alphaImageCropped = computeImages(hsvImage,light_color, dark_color)
			cv2.imwrite(imageFolder+saveName,HSVmaskedImage)
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
		elif guiCommands['mode']=='nextPic':
			i+=1
			guiCommands['mode']='show'
		
		cv2.destroyAllWindows()