import numpy as np
import cv2
import urllib2
import socket
import sys
import math
import os

#you don't actually need this class, but the tutorial used it, so I implemented it. All it does is contain two functions. No biggie.
#It's initialized at the beginning of the main function.
class Processor:
	
	def get_blue(self, img):
		#again, probably didn't need this. Could have just put this code in the main function. I'll probably do that later. Whatevs.
		blue = cv2.split(img)[2]
		return blue

	def get_blue_hue(self, img):
		#filters img based on hsv values of blue
		#may need finetuning based on lighting conditions. Probably not, though.
		hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
		#this is what the LEDs shine, according to photoshop
		#note for future people: photoshop, gimp, and opencv all use different number to represent the hsv values
		#make sure that you convert them to opencv
		blue_vals = [120, 235, 235]
		upper = [140, 255, 255]
		lower = [100, 200, 200]
		#filter to only blue and return image
		only_blue = cv2.inRange(hsv_img, np.array(lower), np.array(upper))
		return only_blue
	
def getDistFromCenter():
	#this is the main image processing function
	#it is only called when the socket connection recieves a 'G'

	#showPrint is used for logging. turn off for competition.
	showPrint = False
	
	"""grab image"""
	opener = urllib2.build_opener()
	page = opener.open(picurl)
	pic =page.read()
	#here, we write the image to disk because it needs to be read into opencv, not simply passed.
	#this could probably be opmitted with the pillow library, but I don't feel like it.
	#that would probably make this faster, especially considering we're running a class 2 SD card.
	#note to self: use class 10 next time.
	fout = open('image.jpg', 'wb')
	fout.write(pic)
	fout.close()

	#read img into opencv format
	img = cv2.imread('image.jpg')
	GlobalWidth = 640
	GlobalHeight = 480

	#optionally resize by commenting out this line. It didn't have much impact, so no biggie.
	resize = False
	if resize: 
		img = cv2.resize(img, (GlobalWidth/2,GlobalHeight/2))
		GlobalWidth = GlobalWidth/2
		GlobalHeight = GlobalHeight/2

	#show images on gui with cv2.imshow()
	if showPrint: cv2.imshow('original_img', img)
	#if showPrint: print 'got image...'

	#grab only blue version and make a copy to work with
	blue_only = processor.get_blue_hue(img)
	goals_img = blue_only.copy()
	
	#grab contours in image with basic search
	contours, hierarchy = cv2.findContours(blue_only, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	#if showPrint: print 'foundContours...'
	
	#if showPrint:
		#blue_only = cv2.resize(blue_only, (GlobalWidth, GlobalHeight))
		#cv2.drawContours(blue_only, contours, -1, (156,156,156), 3)
		#cv2.imshow('all_contours', blue_only)

	#this block of code grabs all the contours above a certain area and then chooses the smallest of them
	os.system('clear')
	area = 0
	idx = -1
	for i,cnt in enumerate(contours):
		#for each contour
		#if showPrint: print cv2.contourArea(cnt)
		#if area is above 800 and below 8k, is probably goal
		if (800 < cv2.contourArea(cnt) < 20000):
			#temporarily grab convex hull and stuf for each contour
			rect = cv2.convexHull(cnt)
			minRect = cv2.minAreaRect(rect)

			
			x1 = int(minRect[0][0])
			y1 = int(minRect[0][1])
			width = minRect[1][0]
			height = minRect[1][1]
			degree = minRect[2]
			if showPrint:

				print 'x1:', x1
				print 'y1:', y1
				print 'width:', width
				print 'height:', height
				print 'degree:', degree
			
			if showPrint:
				pass
				#cv2.drawContours(blue_only, rect, -1, (156,156,156), 8)
				#cv2.polylines(img, np.array(minRectPoints), True, (200,200,200), 20)
				#retval = cv2.boundingRect(rect)
				#print 'retval:', retval
				#cv2.imshow('point_set', blue_only)
			if minRect[1][0]:
				ratio = minRect[1][1] / minRect[1][0]
			else:
				ratio = 0
			if showPrint: print 'ratio', ratio
	
			if ((2.9 < ratio < 3.3) or (0.25 < ratio < 0.37)):
				#if the goal is part of the 3pt one, I only want the inside contour
				#therefore grab the smallest contour that fullfills the ratio
				if showPrint: print 'winning ratio:', ratio

				if (area < cv2.contourArea(cnt)):
					idx = i
					
			"""
			if (area < cnt.size):
				idx = i
			"""
	#if showPrint: print 'idx:', idx
	if (idx != -1):
		#if a goal was found
		if showPrint:		
			cv2.drawContours(goals_img, contours, idx, (50, 255, 60), 3)
			cv2.imshow('rects', goals_img)
		
		#grab an approx rect
		rect = cv2.convexHull(contours[idx])
		if showPrint: 'rect:', rect
		#grab a minimum area rect
		minRect = cv2.minAreaRect(rect)
		
		area = cv2.contourArea(contours[idx])
		
		if showPrint:
			pass
			#cv2.rectangle(goals_img, 
		#this is a good rect to use
		#find centre point
		#apparently the format is as follows: botLeftX, botLeftY, Width, Height
		
		x1 = int(minRect[0][0])
		y1 = int(minRect[0][1])
		width = minRect[1][0]
		height = minRect[1][1]
		degree = minRect[2]

		if showPrint: print 'DEGREE:', degree
		# if opencv accidentally inverts the rectangle, this fixes it
		if width < height:
			width, height = height, width
		
		# read the included whitepaper to fully understand this.
		#it's simply a ratio of the pixel width to the actual width
		if showPrint: print width
		dist_FOV = 4.25*GlobalWidth/width
		#this uses a little bit of trig to get the distance to the wall
		if showPrint: print dist_FOV
		dist_to_wall = (dist_FOV/2) / 0.41237445509
		
		#this number is then corrected for error based on a function from excel
		# and then finally rounded to milli-feet
		new_dist_to_wall = dist_to_wall * (0.178195*np.log(dist_to_wall) + 0.6357449)
		dist_to_wall = int(new_dist_to_wall*1000)
		if showPrint:
			print 'CALCULATED DIST', new_dist_to_wall
		#correct ratio for 3 pt goal is almost exactly 3 +- 0.1
		ratio = height/width
		#if showPrint: print "h:", height, "width:", width, "ratio:", ratio
		#for some reason, the point x1,y1 is the center, not a corner. It should be, but I won't question it.
		#draw centre point
		if showPrint: 
			cv2.circle(goals_img, (x1,y1), 6, (244,255,255))
			cv2.line(goals_img, (GlobalWidth/2, GlobalHeight), (GlobalWidth/2, 0), (200,200,200)) 
			cv2.imshow('rects', goals_img)

		#now get distance from center of screen
		#320 happens to be half of the width of the screen
		#should probably use a variable to work with diff screens, but whatever
		dist = 0
		if (x1 < GlobalWidth/2):
			dist = -(GlobalWidth/2 - x1)
		elif (x1 > GlobalWidth/2):
			dist = (GlobalWidth/2 - (GlobalWidth - x1))
		elif (x1 == GlobalWidth/2):
			dist = 0	


		#return all that info in format: distFromCenter, x1, y1, distToWall
		#this function also returns the finished image, even though it is never used in the main loop
		return str(dist) + ',' + str(x1) + ',' + str(y1) + ',' + str(dist_to_wall), goals_img
	else:
		#can't see anything: should report error
		return 'n', goals_img

	

if __name__ == '__main__':
	processor = Processor()
	
	picurl = 'http://10.39.46.11/jpg/1/image.jpg'

	#debugging is True if you want to bypass the socket connection and just work on image processing code
	debugging = True
	if (debugging == False):

		#create the socket server
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serv_addr = ('10.39.46.12', 10000)
		print 'starting server on: ', serv_addr[0], ':', serv_addr[1]

		sock.bind(serv_addr)
		sock.listen(1)
		conn = None
		while True:
			try:
				#wait for connection- script will hang here until connection received
				conn, cli_addr = sock.accept()
				print 'connection from: ', cli_addr

				#on connection, wait for 'g' 
				try:
					while True:
						try:
							#hang here for data
							recvd = conn.recv(4096)
							print recvd
							
							#this line used to be if (recvd == 'G'), but when testing with putty, I also
							#received newlines, so this will work regardless
							if ('G' in recvd):
								#run command
								result, img = getDistFromCenter()
								print result
								test = conn.send(str(result))
								print 'sent:', test
							else:
								print 'not G'
						except:
							print ' exception:', sys.exc_info()[0]
							conn.close()
							print 'conn closed'
							break

				finally:
					print 'connection closed'
					conn.close()

			except KeyboardInterrupt:
				print 'LOSING'
				if conn: conn.close()
				break
	else:
		#are debugging
		while True:
			try:
				result, goals_img =  getDistFromCenter()
				print 'SENDINGSENDINGSENDING:  ', result
				#cv2.imshow('testing', goals_img)	
				cv2.waitKey(1)		

			except KeyboardInterrupt:
				break
