import numpy as np
import cv2
import urllib2
import cv
import socket
import sys

#you don't actually need this class, but the tutorial used it, so I implemented it. All it does is contain two functions. No biggie.
#It's initialized at the beginning of the main function.
class Processor:
	
	def get_blue(self, img):
		#again, probably didn't need this. Could have just put this code in the main function. I'll probably do that later. Whatevs.
		blue = cv2.split(img)[2]
		return blue

	def get_blue_hue(self, img):
		#filters img  based on hsv values of blue
		#may need finetuning based on lighting conditions. Probably not, though.
		hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
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
	showPrint = True
	
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

	#optionally resize by commenting out this line. It didn't have much impact, so no biggie.
	#img = cv2.resize(img, (320,240))
	#show images on gui with cv2.imshow()
	#cv2.imshow('original_img', img)
	if showPrint: print 'got image...'

	#grab only blue version and make a copy to work with
	blue_only = processor.get_blue_hue(img)
	goals_img = blue_only.copy()
	
	#grab contours in image with basic search
	contours, hierarchy = cv2.findContours(blue_only, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	if showPrint: print 'foundContours...'
	

	#this block of code grabs all the contours above a certain area and then chooses the smallest of them
	area = 0
	idx = 0
	for i,cnt in enumerate(contours):
		#for each contour
		if (cv2.contourArea(contours[i]) > 10000):
			#if area is above 10k, is probably goal
			#now grab the smallest one
			if (area < cnt.size):
				idx = i

	print 'idx:', idx
	if idx > 0:
		#if a goal wa found
		
		#cv2.drawContours(goals_img, contours, idx, (50, 255, 60), 3)
		#cv2.imshow('test', goals_img)
	
		#grab an approx rect
		rect = cv2.convexHull(contours[idx])

		#grab a minimum area rect
		minRect = cv2.minAreaRect(rect)

		area = cv2.contourArea(contours[idx])
		
		#convert the area of the goal to a distance from the bot via a linear function
		#derive this via point-slope formula
		dist_to_wall = int(((area/1000.) - 86.73)/-4.36)
		
		if showPrint: print 'area:', area, 'dist:', dist_to_wall

		#this is a good rect to use
		#find centre point
		x1 = int(minRect[0][0])
		x2 = int(minRect[1][0])
		y1 = int(minRect[0][1])
		y2 = int(minRect[1][1])

		#for some reason, the point x1,y1 is the center, not a corner. It should be, but I won't question it.
		centerPoint = (x1,y1)
		#draw centre point
		#cv2.circle(goals_img, centerPoint, 6, (244,255,255))

		#now get distance from center of screen
		#320 happens to be half of the width of the screen
		#should probably use a variable to work with diff screens, but whatever
		dist = 0
		if (x1 < 320):
			dist = -(320 - x1)			
		elif (x1 > 320):
			dist = x1 -320 
		elif (x1 == 320):
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
	debugging = False
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
				print result
				cv2.imshow('testing', goals_img)			

			except KeyboardInterrupt:
				break
