# import the necessary packages
import argparse
import cv2
 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
    help="Path to the input image")
ap.add_argument("-c", "--cascade",
    default="../cascade_xml/stop_sign.xml",
    help="Path to STOP sign detector haar cascade")
args = vars(ap.parse_args())


# load the input image and convert it to grayscale
image = cv2.imread(args["image"])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
 
# load the object detector Haar cascade, then detect objects in the input image
detector = cv2.CascadeClassifier(args["cascade"])
rects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(5, 5))

# loop over the objects and draw a rectangle surrounding each
for (i, (x, y, w, h)) in enumerate(rects):
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
    cv2.putText(image, "Object #{}".format(i + 1), (x, y - 8),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
 
# show the detected object
cv2.imshow( args["image"], image)
cv2.waitKey(0)

