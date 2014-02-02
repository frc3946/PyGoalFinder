# -*- coding: utf-8 -*-
"""
Created on Sun Feb 02 11:42:37 2014

@author: Jeff

Use this program to probe an image to find the max and min hsv values
After the image opens, click on as many locations on the image as possible that
are regions that you want the mask to keep
"""

import cv2


def evento_mouse(event, x, y, flags, param):
    
    if event == cv2.EVENT_FLAG_LBUTTON:
        height = y
        width = x
        H = hsv_img[height][width][0]
        S = hsv_img[height][width][1]
        V = hsv_img[height][width][2]
        evento_mouse.maxH = max(H, evento_mouse.maxH)
        evento_mouse.maxS = max(S, evento_mouse.maxS)
        evento_mouse.maxV = max(V, evento_mouse.maxV)
        evento_mouse.minH = min(H, evento_mouse.minH)
        evento_mouse.minS = min(S, evento_mouse.minS)
        evento_mouse.minV = min(V, evento_mouse.minV)
        print "(",x,",",y,") H:",H, "S: ",  S, "V: ", V
        print "Max: ",  evento_mouse.maxH, evento_mouse.maxS, evento_mouse.maxV 
        print "Min: ",  evento_mouse.minH, evento_mouse.minS, evento_mouse.minV 
              
        
imagen=cv2.imread('C:\Files\Work\FIRST\image3.jpg')
cv2.imshow('original_img', imagen)
cv2.setMouseCallback('original_img',evento_mouse)
hsv_img = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
evento_mouse.maxH = 0
evento_mouse.maxS = 0
evento_mouse.maxV = 0
evento_mouse.minH = 255
evento_mouse.minS = 255
evento_mouse.minV = 255
cv2.waitKey(0) 
cv2.destroyAllWindows()