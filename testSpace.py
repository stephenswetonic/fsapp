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
    def __init__(self, image, out_file):
        threading.Thread.__init__(self)
        self.block = image
        self.out_file = out_file
    
    def get_blur_map(self, win_size=10, sv_num=3):
        #print(self.block)
        img = cv2.cvtColor(self.block, cv2.COLOR_BGR2GRAY)
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
        cv2.imwrite(self.out_file, (1-blur_map)*255)

        rgba = cv2.cvtColor(self.block, cv2.COLOR_RGB2RGBA)
        alpha_mask = (1-blur_map*255)
        rgba[:, :, 3] = alpha_mask

        cv2.imwrite('alpha.png', rgba)



        return blur_map

    def run(self):
        #print("Starting sequence " + str(self.sequenceNumber))
        self.get_blur_map()

# images is a list of cv2 images
def align_images(images):

  # First image in the array used as a template
  im1 =  images[0]

  returnImages = []
  returnImages.append(im1)

  for img in images:
    im2 =  img

    # Convert images to grayscale
    im1_gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
    im2_gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

    sz = im1.shape
    warp_mode = cv2.MOTION_TRANSLATION # Can be MOTION.HOMOGRAPHY

    if warp_mode == cv2.MOTION_HOMOGRAPHY :
      warp_matrix = np.eye(3, 3, dtype=np.float32)
    else :
      warp_matrix = np.eye(2, 3, dtype=np.float32)

    number_of_iterations = 5000

    # Specify the threshold of the increment
    termination_eps = 1e-10

    # Termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations,  termination_eps)

    # Run the ECC algorithm. The results are stored in warp_matrix.
    (cc, warp_matrix) = cv2.findTransformECC (im1_gray,im2_gray,warp_matrix, warp_mode, criteria)

    if warp_mode == cv2.MOTION_HOMOGRAPHY :
    # Use warpPerspective for Homography
      im2_aligned = cv2.warpPerspective (im2, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
    else :
    # Use warpAffine for Translation, Euclidean and Affine
      im2_aligned = cv2.warpAffine(im2, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
      returnImages.append(im2_aligned)

  return returnImages





# images should be a list of file paths
def focus_stack(images, out_files):
    blocksize = 10
    svdNum = 3
    cv2_images = []
    aligned_images = []

    for i in range(len(images)):
        cv2_images.append(cv2.imread(images[i], cv2.IMREAD_COLOR))

    # Align
    aligned_images = align_images(cv2_images)


    images_left = len(images)
    index = 0
    toMake = 0
    thread_count = multiprocessing.cpu_count()

    while (images_left > 0):
        thread_group = []
        toMake = min(images_left, thread_count)

        for i in range(toMake):
            thread_group.append(FSProcessor(aligned_images[i], out_files[i]))
            ++index

        for thread in thread_group:
            thread.start()
        for thread in thread_group:
            thread.join()

        images_left -= toMake


start = time.time()
threads = multiprocessing.cpu_count()
print(threads)
images = ['images/tie_near.jpg', 'images/tie_middle.jpg', 'images/tie_far.jpg']
outs = ['images/tie_nearF.png', 'images/tie_middleF.png', 'images/tie_farF.png']


focus_stack(images, outs)

end = time.time()
print(end - start)

# out_file = cv2.imread("images/testoutput.jpg")

# #displaying an image
# cv2.imshow('Image', out_file)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
