# coding: utf-8
from tkinter import *
from threading import Thread
#from PIL import Image, ImageTk
import queue
import string
import time
from multiprocessing import Process, Value, Queue
from setup import *

global GUI_Message

def guiThread():
	#print("setup 1: "+str(networker.getSetup()))
	root = Tk()
	root.geometry("1000x300+0+0")
	gui = Window(root)
	#root.mainloop()
	while 1:
		#print("Names: "+str(networker.getClientNames()))
		gui.updateStatusUpper("Mode: "+guiCommands["mode"])
		gui.updateStatusLower("File: "+guiCommands["loadedFile"])
		#selectedClient=gui.selectClientValue.get()
		root.update()
		time.sleep(0.1)

class Window(Frame):
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.master = master
		self.init_window()
		self.runGUI=True

	#Creation of init_window
	def init_window(self):   
			self.master.title("Green Screen Adjustment")
			# allowing the widget to take the full space of the root window
			self.pack(fill=BOTH, expand=1)
			slider_Length=200
			SetRow=0
			self.HdownLabel=Label(self, text="low H Value").grid(row=SetRow, column=0)
			self.sliderHdown = Scale(self, orient='horizontal', from_=0, to=255, length=slider_Length, command=self.update)
			self.sliderHdown.grid(row=SetRow, column=1, columnspan=2)
			self.sliderHdown.set(guiCommands['hValueL'])

			self.SdownLabel=Label(self, text="low S Value").grid(row=SetRow, column=3)
			self.sliderSdown = Scale(self, orient='horizontal', from_=0, to=255, length=slider_Length, command=self.update)
			self.sliderSdown.grid(row=SetRow, column=4, columnspan=2)
			self.sliderSdown.set(guiCommands['sValueL'])
			
			self.rotateLabel=Label(self, text="low V Value").grid(row=SetRow, column=6)
			self.sliderVdown = Scale(self, orient='horizontal', from_=0, to=255, length=slider_Length, command=self.update)
			self.sliderVdown.grid(row=SetRow, column=7, columnspan=2)
			self.sliderVdown.set(guiCommands['vValueL'])

			SetRow+=1
			self.HupLabel=Label(self, text="high H Value").grid(row=SetRow, column=0)
			self.sliderHup = Scale(self, orient='horizontal', from_=0, to=255, length=slider_Length, command=self.update)
			self.sliderHup.grid(row=SetRow, column=1, columnspan=2)
			self.sliderHup.set(guiCommands['hValueH'])

			self.SupLabel=Label(self, text="high S Value").grid(row=SetRow, column=3)
			self.sliderSup = Scale(self, orient='horizontal', from_=0, to=255, length=slider_Length, command=self.update)
			self.sliderSup.grid(row=SetRow, column=4, columnspan=2)
			self.sliderSup.set(guiCommands['sValueH'])
			
			self.VupLabel=Label(self, text="high V Value").grid(row=SetRow, column=6)
			self.sliderVup = Scale(self, orient='horizontal', from_=0, to=255, length=slider_Length, command=self.update)
			self.sliderVup.grid(row=SetRow, column=7, columnspan=2)
			self.sliderVup.set(guiCommands['vValueH'])
			
			SetRow+=1

			self.upperStatusText=StringVar()
			self.statusLabelUpper=Label(self, textvariable=self.upperStatusText).grid(row=SetRow, column=0,columnspan=2)
			self.lowerStatusText=StringVar()
			self.statusLabelLower=Label(self, textvariable=self.lowerStatusText).grid(row=SetRow, column=2,columnspan=4)
			SetRow+=1
			SetCol=0
			self.nextPicText=StringVar()
			Button(self, textvariable=self.nextPicText, command=self.nextPicSwitch).grid(row=SetRow, column=SetCol,columnspan=2)
			self.nextPicText.set("Next Pic")
			SetCol+=2
			self.previousPicText=StringVar()
			Button(self, textvariable=self.previousPicText, command=self.previousPicSwitch).grid(row=SetRow, column=SetCol,columnspan=2)
			self.previousPicText.set("Previous Pic")
			SetCol+=2
			Button(self, text="Save Settings", command=self.save).grid(row=SetRow, column=SetCol,columnspan=1)
			SetCol+=1
			#SetRow+=1
			#SetCol=0
			Button(self, text="Exit", command=self.client_exit).grid(row=SetRow, column=SetCol,columnspan=2)
			SetCol+=2
			Button(self, text="Select Folder", command=self.selectFolder).grid(row=SetRow, column=SetCol,columnspan=2)
			SetRow+=1
			self.settingsText=StringVar()
			self.settingsLabel=Label(self, textvariable=self.settingsText).grid(row=SetRow, column=0,columnspan=9)
			
	def updateStatusLower(self,statusLower):
		self.lowerStatusText.set(statusLower)
		
	def updateStatusUpper(self,statusUpper):
		self.upperStatusText.set(statusUpper)

	def updateSettings(self,settingsText):
		self.settingsText.set(settingsText)
		

	def save(self):
		print("save settings")
		f = open("setup.py", "w")
		f.write("guiCommands="+str(guiCommands))
		f.close()

	def selectFolder(self):
		print("Select Folder")
		folderName= filedialog.askdirectory()
		guiCommands['imageFolder']=folderName
		print("folder: ",folderName)

	def nextPicSwitch(self):
		guiCommands['mode']="nextPic"
		print("Mode: ",guiCommands['mode'])
			
	def previousPicSwitch(self):
		guiCommands['mode']="previousPic"
		print("Mode: ",guiCommands['mode'])

	def update(self,value):
		guiCommands['hValueL']=self.sliderHdown.get()
		guiCommands['sValueL']=self.sliderSdown.get()
		guiCommands['vValueL']=self.sliderVdown.get()
		guiCommands['hValueH']=self.sliderHup.get()
		guiCommands['sValueH']=self.sliderSup.get()
		guiCommands['vValueH']=self.sliderVup.get()

	def client_exit(self):
		guiCommands['mode']="stop"
		guiCommands['runLoop']=False
		print("exit pressed")
		time.sleep(1)
		#SetLightTo(0)
		self.runGUI=False
		exit()
