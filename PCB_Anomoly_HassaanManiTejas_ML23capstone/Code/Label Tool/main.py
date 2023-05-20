import tkinter as tk
from tkinter import messagebox
from tkinter import *
from PIL import Image
from PIL import ImageTk
import os
import numpy as np
import cv2
import imutils

""" Notes
Assumes defect and template images are same size -- I'm too lazy to account for this
"""


""" Dependencies
- sudo apt-get install python3-pil python3-pil.imagetk -- there should be a pip3 version
- tkinter, opencv, nunpy, imutils -- just use pip/pip3 for those
"""


""" Program parameters
enter absolute paths -- assumes numbering scheme for images 1-num_images
"""
defect_path = "/home/manip/Desktop/UMD/Spring 2023/ENEE 439D/Defect Marker/defect"
nodefect_path = "/home/manip/Desktop/UMD/Spring 2023/ENEE 439D/Defect Marker/nodefect"
save_root_defect = "/home/manip/Desktop/UMD/Spring 2023/ENEE 439D/Defect Marker/defect_cropped"
save_root_nodefect = "/home/manip/Desktop/UMD/Spring 2023/ENEE 439D/Defect Marker/nodefect_cropped"
do_img_alignment = True


num_images = 3
file_ext = ".JPG"
geom = (2400, 2400)
crop_w, crop_h = 80, 80



# global vars
img_cnt = -1
defect_images = []
nodefect_images = []

defect_images_disp = []
nodefect_images_disp = []

defect_clicks = []

def display_img():
    global img_cnt
    img_cnt += 1
    if img_cnt >= num_images:
        tk.messagebox.showinfo(title=None, message="Done processing images!")
        process_images()
        root.quit()
        return
    canvas.delete('all')
    canvas.create_image(0,0,anchor=NW,image=defect_images_disp[img_cnt])
    defect_clicks.append([])

def process_images():
    cnt = 1
    for i in range(0, num_images):
        defect = defect_images[i]
        nodefect = nodefect_images[i]
        clicks = defect_clicks[i]

        h,w,c = defect.shape

        for x, y in clicks:
            i_x, i_y = x - crop_w // 2, y - crop_h // 2
            i_x = i_x if i_x >= 0 else 0
            i_y = i_y if i_y >= 0 else 0

            i_x_2, i_y_2 = x + crop_w // 2, y + crop_h // 2
            i_x_2 = i_x_2 if i_x_2 < w else w
            i_y_2 = i_y_2 if i_y_2 < h else h

            new_defect = defect[i_y:i_y_2, i_x:i_x_2]
            new_nodefect = nodefect[i_y:i_y_2, i_x:i_x_2]

            # add padding if needed
            defect_res = np.full((crop_h,crop_w, 3), (0,0,0), dtype=np.uint8)
            nodefect_res = np.full((crop_h,crop_w, 3), (0,0,0), dtype=np.uint8)

            defect_res[0:new_defect.shape[0], 0:new_defect.shape[1]] = new_defect
            nodefect_res[0:new_nodefect.shape[0], 0:new_nodefect.shape[1]] = new_nodefect

            cv2.imwrite(os.path.join(save_root_defect, str(cnt) + file_ext), defect_res)
            cv2.imwrite(os.path.join(save_root_nodefect, str(cnt) + file_ext), nodefect_res)

            cnt += 1

def canvas_click(event):
    global img_cnt
    x, y = event.x, event.y
    defect_clicks[img_cnt].append((x, y))
    canvas.create_oval(x,y,x,y,fill="red",outline="red", width=20,)

def align_img(img, template):
    maxFetaures = 500
    keepPercent = .2

    imageGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    templateGray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    orb = cv2.ORB_create(maxFetaures)
    (kpsA, descsA) = orb.detectAndCompute(imageGray, None)
    (kpsB, descsB) = orb.detectAndCompute(templateGray, None)
    # match the features
    method = cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
    matcher = cv2.DescriptorMatcher_create(method)
    matches = matcher.match(descsA, descsB, None)

    matches = sorted(matches, key=lambda x:x.distance)
    # keep only the top matches
    keep = int(len(matches) * keepPercent)
    matches = matches[:keep]

    ptsA = np.zeros((len(matches), 2), dtype="float")
    ptsB = np.zeros((len(matches), 2), dtype="float")
    # loop over the top matches
    for (i, m) in enumerate(matches):
        # indicate that the two keypoints in the respective images
        # map to each other
        ptsA[i] = kpsA[m.queryIdx].pt
        ptsB[i] = kpsB[m.trainIdx].pt
                
    (H, mask) = cv2.findHomography(ptsA, ptsB, method=cv2.RANSAC)
    # use the homography matrix to align the images
    (h, w) = template.shape[:2]
    aligned = cv2.warpPerspective(img, H, (w, h))
    # return the aligned image
    return aligned


root = tk.Tk()
root.geometry(str(geom[0]) + "x" + str(geom[1]))
canvas = tk.Canvas(root, bg="white", width=geom[0], height=geom[1] * .8)
canvas.bind("<Button-1>", canvas_click)
canvas.pack()

nextBtn = Button(text="Next Image", command=display_img)
nextBtn.pack(side = BOTTOM, fill=BOTH)

# read in files
for i in range(1, num_images + 1):
    # cv2 images
    defect = cv2.imread(os.path.join(defect_path, str(i) + file_ext))
    nodefect = cv2.imread(os.path.join(nodefect_path, str(i) + file_ext))

    # if alignment is desried
    if align_img:
        defect = align_img(defect, nodefect)

    defect_images.append(defect)
    nodefect_images.append(nodefect)

    # display images
    blue,green,red = cv2.split(defect)
    defect = cv2.merge((red,green,blue))
    im = Image.fromarray(defect)
    imgtk = ImageTk.PhotoImage(image=im)
    defect_images_disp.append(imgtk)

    blue,green,red = cv2.split(nodefect)
    nodefect = cv2.merge((red,green,blue))
    im = Image.fromarray(nodefect)
    imgtk = ImageTk.PhotoImage(image=im)
    nodefect_images_disp.append(imgtk)

# display first image
display_img()

root.mainloop()



