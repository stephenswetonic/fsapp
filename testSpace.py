import cv2
import numpy as np
import time
import threading
import multiprocessing
#-1 no alpha
#0 grayscale
#1 Alpha


#Start of blur map process in python
blocksize = 10
svdNum = 3
originalWidth = 0
originalHeight = 0

# img = cv2.imread("images/flower.jpeg", 0)
# originalWidth = img.shape[1]
# originalHeight = img.shape[0]
# blurMap = np.zeros([originalHeight, originalWidth]) # 2D array of zeros  

# padded_img = cv2.copyMakeBorder(img, blocksize, blocksize, blocksize, blocksize, cv2.BORDER_REFLECT)

# maxSV = 0
# minSV = 1

class FSProcessor(threading.Thread):
    def __init__(self, image):
        threading.Thread.__init__(self)
        self.block = image
    
    def get_blur_map(self, win_size=10, sv_num=3):
        img = self.block
        new_img = np.zeros((img.shape[0]+win_size*2, img.shape[1]+win_size*2))
        for i in range(new_img.shape[0]):
            for j in range(new_img.shape[1]):
                if i<win_size:
                    p = win_size-i
                elif i>img.shape[0]+win_size-1:
                    p = img.shape[0]*2-i
                else:
                    p = i-win_size
                if j<win_size:
                    q = win_size-j
                elif j>img.shape[1]+win_size-1:
                    q = img.shape[1]*2-j
                else:
                    q = j-win_size
                #print p,q, i, j
                new_img[i,j] = img[p,q]

        #cv2.imwrite('test.jpg', new_img)
        #cv2.imwrite('testin.jpg', img)
        blur_map = np.zeros((img.shape[0], img.shape[1]))
        max_sv = 0
        min_sv = 1
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                block = new_img[i:i+win_size*2, j:j+win_size*2]
                u, s, v = np.linalg.svd(block)
                top_sv = np.sum(s[0:sv_num])
                total_sv = np.sum(s)
                sv_degree = top_sv/total_sv
                if max_sv < sv_degree:
                    max_sv = sv_degree
                if min_sv > sv_degree:
                    min_sv = sv_degree
                blur_map[i, j] = sv_degree
        #cv2.imwrite('blurmap.jpg', (1 - blur_map) * 255)

        blur_map = (blur_map-min_sv)/(max_sv-min_sv)
        #cv2.imwrite('blurmap_norm.jpg', (1-blur_map)*255)
        return blur_map

    def run(self):
        print("Starting sequence " + str(self.sequenceNumber))
        self.get_blur_map()

    

# def get_blur_map_numba(image_file, win_size=10, sv_num=3):
#     img = image_file
#     new_img = np.zeros((img.shape[0]+win_size*2, img.shape[1]+win_size*2))
#     for i in range(new_img.shape[0]):
#         for j in range(new_img.shape[1]):
#             if i<win_size:
#                 p = win_size-i
#             elif i>img.shape[0]+win_size-1:
#                 p = img.shape[0]*2-i
#             else:
#                 p = i-win_size
#             if j<win_size:
#                 q = win_size-j
#             elif j>img.shape[1]+win_size-1:
#                 q = img.shape[1]*2-j
#             else:
#                 q = j-win_size
#             #print p,q, i, j
#             new_img[i,j] = img[p,q]

#     #cv2.imwrite('test.jpg', new_img)
#     #cv2.imwrite('testin.jpg', img)
#     blur_map = np.zeros((img.shape[0], img.shape[1]))
#     max_sv = 0
#     min_sv = 1
#     for i in range(img.shape[0]):
#         for j in range(img.shape[1]):
#             block = new_img[i:i+win_size*2, j:j+win_size*2]
#             u, s, v = np.linalg.svd(block)
#             top_sv = np.sum(s[0:sv_num])
#             total_sv = np.sum(s)
#             sv_degree = top_sv/total_sv
#             if max_sv < sv_degree:
#                 max_sv = sv_degree
#             if min_sv > sv_degree:
#                 min_sv = sv_degree
#             blur_map[i, j] = sv_degree
#     #cv2.imwrite('blurmap.jpg', (1 - blur_map) * 255)

#     blur_map = (blur_map-min_sv)/(max_sv-min_sv)
#     #cv2.imwrite('blurmap_norm.jpg', (1-blur_map)*255)
#     return blur_map


start = time.time()
threads = multiprocessing.cpu_count()
print(threads)
input = cv2.imread("images/flower.jpeg", cv2.IMREAD_GRAYSCALE)

# half = input.shape[1] // 2
# left_block = input[:, :half]
# right_block = input[:, half:]



# for i in range(threads):
#     FSProcessors.append(FSProcessor(i, image_blocks[i]))

# for fsp in FSProcessors:
#     fsp.start()

# For each block:
#   spawn threaded function
#   pass each block
#   join
#testBlurMap = get_blur_map_numba(input)
#cv2.imwrite("images/testoutput.jpg", (1-testBlurMap)*255)
end = time.time()
print(end - start)

out_file = cv2.imread("images/testoutput.jpg")

#displaying an image
# cv2.imshow('Image', out_file)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
