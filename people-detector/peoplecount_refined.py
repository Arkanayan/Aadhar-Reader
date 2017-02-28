# import the necessary packages
import argparse
import datetime
import imutils
import time
import cv2
# import MySQLdb
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pylab import *
# import sqlite3
from imutils.object_detection import non_max_suppression

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min_area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())
 
# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
	camera = cv2.VideoCapture(0)
	time.sleep(0.25)
 
# otherwise, we are reading from a video file
else:
	camera = cv2.VideoCapture(args["video"])


# db = MySQLdb.connect("localhost","root","password","people_count" )
# cursor = db.cursor()
# cursor.execute("DROP TABLE IF EXISTS pplnum")

# sql = """CREATE TABLE pplnum (Timepassed INT,  Count INT )"""
# cursor.execute(sql)

#initializing the graph figure
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

xar=[]
yar=[]
	
def animate(i):
    ax1.clear()
    ax1.plot(xar,yar)


# initialize the first frame in the video stream
firstFrame = None


# initialize the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

initial_time = datetime.datetime.now()

# loop over the frames of the video
while True:
	# grab the current frame and initialize the occupied/unoccupied
	# text
	(grabbed, frame) = camera.read()
	text = "Unoccupied"
	num_people = 0
 
	# if the frame could not be grabbed, then we have reached the end
	# of the video
	if not grabbed:
		break
 
	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)
 
	# if the first frame is None, initialize it
	if firstFrame is None:
		firstFrame = gray
		continue
    # compute the absolute difference between the current frame and
	# first frame
	frameDelta = cv2.absdiff(firstFrame, gray)
	thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
 
	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image 
      #Yet to find out the exact syntax meaning of this
	thresh = cv2.dilate(thresh, None, iterations=2)
	(_,cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
 
	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < args["min_area"]:
			continue
 
		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
		roi_frame = frame[y:y+h, x:x+w]
		
		(rects, weights) = hog.detectMultiScale(roi_frame, winStride=(1, 1),
		padding=(2, 2), scale=1.05)

		rects = np.array([[x_, y_, x_ + w_, y_ + h_] for (x_, y_, w_, h_) in rects])
		pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)

		for (xA, yA, xB, yB) in pick:
			cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)
			text = "Occupied"
			num_people = num_people + 1

	# draw the text and timestamp on the frame
	cv2.putText(frame, "Room Status: {}, Count: {}".format(text, num_people), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	#cv2.putText(frame, "Count: {}".format(num_people), (10, 20),
		#cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

	current_time = datetime.datetime.now()
	time_diff = int((current_time - initial_time).total_seconds())
 
	# show the frame and record if the user presses a key
	cv2.imshow("Security Feed", frame)
	cv2.imshow("Thresh", thresh)
	cv2.imshow("Frame Delta", frameDelta)
	key = cv2.waitKey(1) & 0xFF

	# try:
	# 	cursor.execute("""INSERT INTO pplnum VALUES (%s,%s)""",(time_diff, num_people))
	# 	db.commit()
	# except:
	# 	db.rollback()

	if (time_diff%5 == 0):
		# cursor.execute("SELECT * FROM pplnum WHERE Timepassed = time_diff")
		# values = cursor.fetchone()
		values = [time_diff, num_people]
		xar.append(values[0])
		yar.append(values[1])

		ani = animation.FuncAnimation(fig, animate, interval = 5000)
 
	# if the `q` key is pressed, break from the lop
	if key == ord("q"):
		break
 
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()