import numpy as np
import cv2
import time, os, operator
from matplotlib import pyplot as plt
from threading import Thread
from GUI import *
from functions import *


preview_scale_factor=0.5
font = cv2.FONT_HERSHEY_SIMPLEX

def getFileList(folder):
	fileList={}
	nameList=[]
	#print("get file list")
	try:
		with os.scandir(folder) as allEntries:
			for entry in allEntries:
				#print("allEntries: "+str(entry.name))
				if entry.name.endswith('.png') and entry.is_file() and not entry.name.startswith('out_') and not entry.name.startswith('alpha_'):
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

def computeImagesHSV(inputImage, light_color,dark_color):
	dimX , dimY = inputImage.shape[:2]
	hsvImage =cv2.cvtColor(inputImage,cv2.COLOR_BGR2HSV)
	HSVmask = cv2.inRange(hsvImage, light_color, dark_color)
	HSVmaskedImage=cv2.bitwise_and(inputImage,inputImage, mask=HSVmask)
	filledHSVmask = np.zeros((dimX, dimY,1), np.uint8)
	(cntsHSVmask, _) = cv2.findContours(HSVmask, cv2.RETR_EXTERNAL, 2)
	cntsHSVmask = sorted(cntsHSVmask, key = cv2.contourArea, reverse = True)[:1]
	if len(cntsHSVmask) > 0:
		cv2.drawContours(HSVmaskedImage, cntsHSVmask, -1, (0, 255, 0), 5)
		box = cv2.boundingRect(cntsHSVmask[0])
		cv2.fillPoly(filledHSVmask,cntsHSVmask,(255,255,255))
		HSVpreviewImage=cv2.bitwise_and(inputImage,inputImage, mask=filledHSVmask)
		cv2.rectangle(HSVmaskedImage,(box[0],box[1]),(box[0]+box[2],box[1]+box[3]),(255,0,0),2)
		alphaImage = cv2.cvtColor(inputImage, cv2.COLOR_BGR2BGRA)
		alphaImage[:,:,3]=filledHSVmask[:,:,0]
		alphaImageCropped=alphaImage[box[1]:box[1]+box[3],box[0]:box[0]+box[2]]
		HSVpreviewImage=HSVpreviewImage[box[1]:box[1]+box[3],box[0]:box[0]+box[2]]
	else:
		print("no contour detected")
	cv2.putText(HSVmaskedImage,str(light_color),(20,40),font,1,(0,255,0), 1,cv2.LINE_AA)
	cv2.putText(HSVmaskedImage,str(dark_color),(20,80),font,1,(0,255,0), 1,cv2.LINE_AA)
	return HSVmaskedImage, HSVpreviewImage, alphaImageCropped

def computeImagesThreshold(inputImage,lowerThreshold,averageCorrection):
	if averageCorrection % 2 == 0:
		averageCorrection += 1
	dimX , dimY = inputImage.shape[:2]
	grayImage = cv2.cvtColor(inputImage, cv2.COLOR_BGR2GRAY)
	#grayImage = cv2.GaussianBlur(grayImage,(averageCorrection,averageCorrection),0)
	#show_smaller_image(grayImage,"gray",preview_scale_factor,500,500)
	totalPixels = dimX * dimY
	averageBrightness=np.sum(grayImage)/totalPixels
	#print("Average Brightness:",averageBrightness)
	#print("Average Correction:",int(averageCorrection))
	#ret, threshImage = cv2.threshold(grayImage,lowerThreshold,upperThreshold,cv2.THRESH_BINARY)
	lowerThresholdCorrected = int(lowerThreshold + averageCorrection*averageBrightness)
	if lowerThresholdCorrected > 255:
		lowerThresholdCorrected = 255
	ret, threshImage = cv2.threshold(grayImage,lowerThreshold,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	#ret, threshImage = cv2.threshold(grayImage,lowerThresholdCorrected,255,cv2.THRESH_BINARY)
	#show_smaller_image(threshImage,"thresh",preview_scale_factor,1000,500)
	#threshImage = cv2.adaptiveThreshold(grayImage,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,int(averageCorrection),-lowerThreshold)
	#threshImage = cv2.adaptiveThreshold(grayImage,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,int(averageCorrection),-lowerThreshold)
	ThreshMaskedImage=cv2.bitwise_and(inputImage,inputImage, mask=threshImage)
	filledThreshMask = np.zeros((dimX, dimY,1), np.uint8)
	(contoursThresh, _) = cv2.findContours(threshImage, cv2.RETR_EXTERNAL, 2)
	contoursThresh = sorted(contoursThresh, key = cv2.contourArea, reverse = True)[:1]
	ThreshPreviewImage=inputImage.copy()
	alphaImage = cv2.cvtColor(inputImage, cv2.COLOR_BGR2BGRA)
	alphaImageCropped = alphaImage.copy()
	if len(contoursThresh) > 0:
		cv2.drawContours(ThreshMaskedImage, contoursThresh[0], -1, (0, 255, 0), 5)
		box = cv2.boundingRect(contoursThresh[0])
		cv2.fillPoly(filledThreshMask,contoursThresh,(255,255,255))
		ThreshPreviewImage=cv2.bitwise_and(inputImage,inputImage, mask=filledThreshMask)
		cv2.rectangle(ThreshMaskedImage,(box[0],box[1]),(box[0]+box[2],box[1]+box[3]),(255,0,0),2)
		alphaImage[:,:,3]=filledThreshMask[:,:,0]
		alphaImageCropped=alphaImage[box[1]:box[1]+box[3],box[0]:box[0]+box[2]]
		ThreshPreviewImage=ThreshPreviewImage[box[1]:box[1]+box[3],box[0]:box[0]+box[2]]
	else:
		print("no contour detected")
	cv2.putText(ThreshMaskedImage,"Threshold: "+str(lowerThreshold)+" Correction: "+str(averageCorrection),(20,40),font,1,(0,255,0), 1,cv2.LINE_AA)
	cv2.putText(ThreshMaskedImage,"ThresholdCorr: "+str(lowerThresholdCorrected)+" Average: "+str(round(averageBrightness)),(20,80),font,1,(0,255,0), 1,cv2.LINE_AA)
	return ThreshMaskedImage, ThreshPreviewImage, alphaImageCropped
