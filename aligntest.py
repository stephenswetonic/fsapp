import numpy as np
import imutils
import cv2

# This program will transform im2 so that it aligns with im1.
# The output is a transformed image that can replace the old im2.

def alignimages(images):

  # First image in the array used as a template
  im1 =  images[0]

  returnImages = []
  returnImages.append(im1)

  for img in images:
    im2 =  img

    # Convert images to grayscale
    im1_gray = cv2.cvtColor(im1,cv2.COLOR_BGR2GRAY)
    im2_gray = cv2.cvtColor(im2,cv2.COLOR_BGR2GRAY)

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


# Show final results
# cv2.imshow("Image 1", im1)
# cv2.imshow("Image 2", im2)
# cv2.imshow("Aligned Image 2", im2_aligned)
# cv2.waitKey(0)

multialigntest = []
multialigntest.append(cv2.imread("images/multialigntest0.jpg"))
multialigntest.append(cv2.imread("images/multialigntest1.jpg"))
multialigntest.append(cv2.imread("images/multialigntest2.jpg"))
multialigntest.append(cv2.imread("images/multialigntest3.jpg"))
multialigntest.append(cv2.imread("images/multialigntest4.jpg"))

print(len(multialigntest))
multialigntest = alignimages(multialigntest)


cv2.imshow("Image 1", multialigntest[0])
cv2.imshow("Image 2", multialigntest[1])
cv2.imshow("Image 3", multialigntest[2])
cv2.imshow("Image 4", multialigntest[3])
cv2.imshow("Image 5", multialigntest[4])
cv2.waitKey(0)



