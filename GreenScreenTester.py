import numpy as np
import cv2
import time, os, operator
from matplotlib import pyplot as plt
from threading import Thread
from GUI import *

preview_scale_factor=0.8
font = cv2.FONT_HERSHEY_SIMPLEX
imageFolder='../GreenscreenPics/'

def getFileList(folder):
	fileList={}
	with os.scandir(folder) as allEntries:
		for entry in allEntries:
			if entry.name.endswith('.png') and entry.is_file():
				#print("allEntries: "+str(entry.name))
				fileList.update([(entry.stat().st_mtime, (entry.name, entry.stat().st_size))])
	sortedList=sorted(fileList.items(),key=operator.itemgetter(0))
	nameList=[]
	for key,value in sortedList:
		#print(key,value[0])
		nameList.append(value[0])
	return nameList

def show_smaller_image(image,title,scale):
        dimX , dimY = image.shape[:2]
        out_image=cv2.resize(image,(int(dimY*scale),int(dimX*scale)),interpolation = cv2.INTER_AREA)
        cv2.imshow(title,out_image)

t_gui=Thread(target=guiThread)
t_gui.daemon=True
t_gui.start()

now=round(time.time(),0)
i=0
runLoop = True
#for i in range(1,100):
while(guiCommands['runLoop']):
	#filename=imageFolder+str(i).zfill(5)+'_1612110796_raw.png'
	#filename=imageFolder+str(i).zfill(5)+'_1612468791_raw.png'
	fileList=getFileList(imageFolder)
	#print('fileList: ',fileList)
	if i<0:
		i=0
	filename=imageFolder+fileList[i]
	print('loading file: '+filename)
	input_image = cv2.imread(filename)
	#cv2.imshow('input',input_image)
	if input_image is not None:
		dimX , dimY = input_image.shape[:2]
		blue,green,red = cv2.split(input_image)
		print('loaded file: '+filename+' i: '+str(i))
		hsv =cv2.cvtColor(input_image,cv2.COLOR_BGR2HSV)
		#orange_red = (12, 255, 255)
		#pink_red= (0, 150, 150)
		#light_green = (80, 30, 50)
		#light_green = (80, 30, 50)
		while guiCommands['mode']=='show':
			time.sleep(0.2)
			#print('waiting')
			cv2.waitKey(1)
			light_green = (int(guiCommands['hValueL']), int(guiCommands['sValueL']), int(guiCommands['vValueL']))
			dark_green = (int(guiCommands['hValueH']), int(guiCommands['sValueH']), int(guiCommands['vValueH']))
			#mask = cv2.inRange(hsv, dark_green, light_green)
			mask = cv2.inRange(hsv, light_green, dark_green)
			#show_smaller_image(input_image,'input_image',preview_scale_factor)
			#show_smaller_image(mask,'mask',preview_scale_factor)
			#cv2.imshow('mask',mask)
			kernel = np.ones((9, 9), np.uint8)
			closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=6)
			#masked_image=cv2.bitwise_and(input_image,input_image, mask=closing)
			masked_image=cv2.bitwise_and(input_image,input_image, mask=mask)

			#(cnts, _) = cv2.findContours(mask, cv2.RETR_EXTERNAL, 2)
			(cnts, _) = cv2.findContours(closing, cv2.RETR_EXTERNAL, 2)
			cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
			# loop over the contours
			#print('length of contours: ',len(cnts))
			if len(cnts) > 0:
				contour_to_show=cnts[0]
				cv2.drawContours(masked_image, contour_to_show, -1, (255, 0, 0), 2)
				box = cv2.minAreaRect(contour_to_show)
				box = cv2.boxPoints(box) 
				box = np.array(box, dtype="int")
				#print("the box is:",box)
				#box_sorted=order_points(box)
			#print("the sorted box is:",box_sorted)
			mask2 = np.zeros((dimX+2,dimY+2),dtype='uint8')
			#cv2.drawContours(masked_image, contour_to_show, -1, ( 0, 255,255), cv2.FILLED)
			#cv2.drawContours(masked_image, contour_to_show, -1, ( 0, 255,255), 2)
			#cv2.fillPoly(masked_image, pts=contour_to_show, color = ( 0, 255,0))
			#cv2.drawContours(masked_image, [box], -1, ( 0, 255,0), 2)
			mask2 = cv2.bitwise_not(mask2)
			#masked_image2 = cv2.bitwise_and(input_image,input_image, mask=mask2)
			cv2.putText(masked_image,str(light_green),(20,40),font,1,(0,255,0), 1,cv2.LINE_AA)
			cv2.putText(masked_image,str(dark_green),(20,80),font,1,(0,255,0), 1,cv2.LINE_AA)
			show_smaller_image(masked_image,'masked '+str(filename),preview_scale_factor)
			#show_smaller_image(closing,'closed '+str(filename),preview_scale_factor)
			#show_smaller_image(mask,'mask '+str(filename),preview_scale_factor)
		#pressedKey=cv2.waitKey(1)
		#print('pressed key: ',pressedKey)
		
		#if pressedKey == 113:
		#	runLoop = False
		if guiCommands['mode']=='savePic':
			colorString=str(light_green)
			colorString=colorString.replace('(','__')
			colorString=colorString.replace(')','__')
			colorString=colorString.replace(',','_')
			saveName='out_'+str(i).zfill(5)+'_'+str(colorString)+'.png'
			cv2.imwrite(imageFolder+saveName,masked_image)
		elif guiCommands['mode']=='previousPic':
			i-=i
			guiCommands['mode']='show'
		elif guiCommands['mode']=='nextPic':
			i+=1
			guiCommands['mode']='show'
		
		cv2.destroyAllWindows()
	else:
		i+=1
	#cv2.destroyAllWindows()