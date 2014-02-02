import numpy as np
import cv2
import urllib2
import socket
import sys
import os

"""
sample images are here:
http://firstforge.wpi.edu/sf/frs/do/viewRelease/projects.wpilib/frs.2014_vision_images.2014_vision_images_supplement
"""

def get_disp_to_wall(GlobalWidth,width):
          # read the included whitepaper to fully understand this.
        #it's simply a ratio of the pixel width to the actual width       
        dist_FOV = 4.25*GlobalWidth/width
        #this uses a little bit of trig to get the distance to the wall        
        dist_to_wall = (dist_FOV/2) / 0.41237445509        
        #this number is then corrected for error based on a function from excel
        # and then finally rounded to milli-feet
        new_dist_to_wall = dist_to_wall * (0.178195*np.log(dist_to_wall) + 0.6357449)
        dist_to_wall = int(new_dist_to_wall*1000)
        return dist_to_wall
    
def get_blue_hue(img):
        #filters img based on hsv values of blue
        #may need finetuning based on lighting conditions. Probably not, though.
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        #this is what the LEDs shine, according to photoshop
        #note for future people: photoshop, gimp, and opencv all use different number to represent the hsv values
        #make sure that you convert them to opencv        
        #upper = [140, 255, 255]
        #lower = [100, 200, 200]
        upper = np.array([255, 255, 160],np.uint8)
        lower = np.array([70, 254, 60],np.uint8)
        #filter to only blue and return image
        only_blue = cv2.inRange(hsv_img, lower, upper)
        return only_blue
    
def getDistFromCenter():
    #this is the main image processing function
    #it is only called when the socket connection recieves a 'G'

    #showPrint is used for logging. turn off for competition.
    showPrint = True

    grabFromCamera = False;    
    
    if (grabFromCamera == True):
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
    else:
        img = cv2.imread('C:\Files\Work\FIRST\image3.jpg')
           
    GlobalWidth, GlobalHeight, depth = img.shape
    #optionally resize by commenting out this line. It didn't have much impact, so no biggie.
    resize = False
    if resize: 
        img = cv2.resize(img, (GlobalWidth/2,GlobalHeight/2))
        GlobalWidth = GlobalWidth/2
        GlobalHeight = GlobalHeight/2

    #show images on gui with cv2.imshow()
    if showPrint: 
        cv2.imshow('orginal', img)
        cv2.waitKey(1)
    #if showPrint: print 'got image...'

    #grab only blue version and make a copy to work with
    blue_only = get_blue_hue(img)
    goals_img = blue_only.copy()
    
    if showPrint: 
        cv2.imshow('contoursImg', blue_only)
        cv2.waitKey(0)
        
    #grab contours in image with basic search
    contours, hierarchy = cv2.findContours(blue_only, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    #if showPrint: print 'foundContours...'

    #this block of code grabs all the contours above a certain area and then chooses the smallest of them
    os.system('clear')    #what does this line do?

    #init our four return values    
    hotGoalResult = 'n'
    targetResult = 'n'   
    aim = 0
    targetDistance = 0
    
    for i,cnt in enumerate(contours):
        #for each contour
        #if showPrint: print cv2.contourArea(cnt)
       
        if showPrint:      
            contoursImg = blue_only.copy()
            cv2.drawContours(contoursImg, contours, i, (156,156,156), 3)
            cv2.imshow('contoursImg', contoursImg)
            print "Contour area:", cv2.contourArea(cnt)
            cv2.waitKey(0)
        
        if (200 < cv2.contourArea(cnt) < 800):
            #temporarily grab convex hull and stuf for each contour
            rect = cv2.convexHull(cnt)
            minRect = cv2.minAreaRect(rect)
            degree = minRect[2]
            #height is always greatest value, howver, we need heigh to always run 
            # up and down. Check degree so see if we need to rotate
            if (abs(degree) < 45):
                width = minRect[1][0]
                height = minRect[1][1]  
            else:
                width = minRect[1][1]
                height = minRect[1][0] 
                
            x1 = int(minRect[0][0])
            y1 = int(minRect[0][1])  
            
            if height:
                ratio = width / height
            else:
                ratio = 0
             #target tape?
            if (.08 < ratio < .8):
               if showPrint: 
                    print 'target tape found at ', minRect[0][0], ", ", minRect[0][1]
               targetDistance = get_disp_to_wall(GlobalWidth, width)
                #now get distance from center of screen
                #320 happens to be half of the width of the screen
                #should probably use a variable to work with diff screens, but whatever
               aim = 0
               if (x1 < GlobalWidth/2):
                   aim = -(GlobalWidth/2 - x1)
               elif (x1 > GlobalWidth/2):
                   aim = (GlobalWidth/2 - (GlobalWidth - x1))
               elif (x1 == GlobalWidth/2):
                   aim = 0 
               
               targetResult = 'Y'            
           
            #hot target tape?
            if (3 < ratio < 10):
                hotGoalResult = 'Y'             
                if showPrint: 
                    print 'hot Goal tape found at ', minRect[0][0], ", ", minRect[0][1]
                    
            if showPrint:
                #print 'x1:', x1
                #print 'y1:', y1
                print 'width:', width
                print 'height:', height
                print 'degree:', degree
                box = cv2.cv.BoxPoints(minRect)
                box = np.int0(box)
                cv2.drawContours(contoursImg,[box],0,(156,156,156),1)               
                #retval = cv2.boundingRect(rect)
                #print 'retval:', retval
                cv2.imshow('contoursImg', contoursImg)
                print 'ratio', ratio
                cv2.waitKey(0)
                
                
    resultString = targetResult + ", " + str(aim) +  ", " + str(targetDistance) +  ", " + hotGoalResult
    if showPrint: 
        print resultString
    #return all that info in format: distFromCenter, x1, y1, distToWall
    #this function also returns the finished image, even though it is never used in the main loop
    return resultString, goals_img
        

if __name__ == '__main__':
    
    cv2.destroyAllWindows() #clear out any windoes from last run    
    
    picurl = 'http://10.39.46.11/jpg/1/image.jpg'

    #debugging is True if you want to bypass the socket connection and just work on image processing code
    debugging = True
    if (debugging == False):

        #create the socket server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv_addr = (socket.gethostbyname(socket.gethostname()), 10000)
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
        #while True:
        #try:
        result, goals_img =  getDistFromCenter()
        cv2.waitKey(1)        

        #except KeyboardInterrupt:
            #break
        
    cv2.destroyAllWindows()
