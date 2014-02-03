Team 3946 is using a Raspberry Pi for vision processing
OpenCV was compiled right on the PI.  See http://mitchtech.net/raspberry-pi-opencv/
The python script was configured to start on boot up.  
The python script starts a tcp server for the CRIO to connect to.
The python script grabs an image from the axis camera.
The image is processed and a text string is generated to indicate
the follow:
1) If the target was found
2) How far away
3) How far from center. 
4) If the hot target was found