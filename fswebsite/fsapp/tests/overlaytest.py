from PIL import Image


outs = ['/Users/stephenswetonic/Documents/FocusStacker/fswebsite/static/images/job27/filterimage0.png', '/Users/stephenswetonic/Documents/FocusStacker/fswebsite/static/images/job27/filterimage1.png', '/Users/stephenswetonic/Documents/FocusStacker/fswebsite/static/images/job27/filterimage2.png']

test = ['/Users/stephenswetonic/Documents/FocusStacker/images/overlaytestbackg.png', '/Users/stephenswetonic/Documents/FocusStacker/images/overlaytestcross.png']

color_fill = Image.open('/Users/stephenswetonic/Documents/FocusStacker/fswebsite/static/images/tie_far.jpg')


background = Image.open('/Users/stephenswetonic/Documents/FocusStacker/fswebsite/static/images/tie_near.jpg')

background.paste(Image.open(outs[0]), mask=Image.open(outs[0]))
# paste outs[0]
#background.show()
#img = Image.open(test[1])

#background.paste(img, (0, 0), mask = img)

for i in range(len(outs) - 1):
    background.paste(Image.open(outs[i+1]), (0,0), mask=Image.open(outs[i+1]))
    #background.show()
background.show()

