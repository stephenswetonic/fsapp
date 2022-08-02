
import numpy as np
import cv2


outs = ['/Users/stephenswetonic/Documents/FocusStacker/fswebsite/static/images/job24/filterimage0.png', '/Users/stephenswetonic/Documents/FocusStacker/fswebsite/static/images/job24/filterimage1.png', '/Users/stephenswetonic/Documents/FocusStacker/fswebsite/static/images/job24/filterimage2.png']

test = ['/Users/stephenswetonic/Documents/FocusStacker/images/overlaytestbackg.png', '/Users/stephenswetonic/Documents/FocusStacker/images/overlaytestcross.png']

overlay_t = cv2.imread(test[1], -1)


background = cv2.imread(test[0], -1)

dest = cv2.addWeighted(background, 1, overlay_t, 1, 0.0)



cv2.imshow('image', dest)
cv2.waitKey(0)