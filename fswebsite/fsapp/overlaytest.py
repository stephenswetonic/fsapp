
import numpy as np
import cv2
from PIL import Image


outs = ['/Users/stephenswetonic/Documents/FocusStacker/fswebsite/static/images/job24/filterimage0.png', '/Users/stephenswetonic/Documents/FocusStacker/fswebsite/static/images/job24/filterimage1.png', '/Users/stephenswetonic/Documents/FocusStacker/fswebsite/static/images/job24/filterimage2.png']

test = ['/Users/stephenswetonic/Documents/FocusStacker/images/overlaytestbackg.png', '/Users/stephenswetonic/Documents/FocusStacker/images/overlaytestcross.png']

background = Image.open(outs[0])

#img = Image.open(test[1])

#background.paste(img, (0, 0), mask = img)

mandelbrot = Image.effect_mandelbrot((2000, 2000), (-3, -2.5, 2, 2.5), 500)
mandelbrot.show()
for i in range(len(outs) - 1):
    background.paste(Image.open(outs[i+1]), (0,0), mask=Image.open(outs[i+1]))
    background.show()

