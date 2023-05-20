import numpy as np
import cv2

import pandas as pd
import tensorflow as tf
import keras as keras
from keras import layers

from skimage.util import random_noise
from skimage.filters import threshold_multiotsu

MODEL_PATH = 'nodefectReconstruct'
nodefect_autoencoder = keras.models.load_model(MODEL_PATH)

def process_pcb_img(img, preprocessBool=True):
  if not preprocessBool: 
    img[img > 255/2] = 255.
    img[img < 255/2] = 0.
    img = (255 - img)/255
    r,g,b = cv2.split(img)
    img = r
    
  if preprocessBool: 
    img = preprocess(img)
    img[img > 0.5] = 1.
    img[img < 0.5] = 0.
  
  cutup = cutImageUp(img, 80, 80)
  prediction = nodefect_autoencoder.predict(cutup, verbose=1)
  prediction = np.reshape(prediction, np.shape(prediction)[:-1])
  h, w = img.shape

  # scale up images
  prediction = [img for img in prediction]
  cutup = [img for img in cutup]

  pred_full = stitchTogether(prediction, w, h)
  #pred_full[pred_full > 0.9] = 1.
  #pred_full[pred_full < 0.9] = 0.
 
  original_img = stitchTogether(cutup, w, h)
  difference = np.subtract(original_img, pred_full)

  return pred_full * 255, difference * 255, img * 255

# function to add Gaussian noise to image
def addNoise(img, noiseFactor):
  h = len(img)
  w = len(img[0])
  noise_img = 255*random_noise(img, mode='s&p',amount=noiseFactor)
  return noise_img

def preprocess(img, noise=False, noiseFactor=None):
  rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
  r,g,b = cv2.split(rgb_img)
  for i in range(len(g)):
    for j in range(len(g[i])):
      g[i][j] = 0

  rgb = np.dstack((b,g,r))

  hsv_img = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
  h,s,v = cv2.split(hsv_img)
  hsv_split = np.concatenate((h,s,v),axis=1)

  thresholds = threshold_multiotsu(v, classes=3)
  if noise: v = addNoise(v, noiseFactor)

  # Using the threshold values, we generate the three regions.
  regions = np.digitize(v, bins=thresholds)

  return regions

def cutImageUp(img, w, h):
  rowRange = range(0, len(img)//w * w, w)
  colRange = range(0, len(img[0])//h * h, h)
  cutup = np.zeros(((len(rowRange)) * (len(colRange)), w, h, 1))
  index = 0
  for (ri, i) in enumerate(rowRange):
    for (ci, j) in enumerate(colRange):
      cutup[index] = np.reshape(img[i : (i + w), j : (j + h)], (w, h, 1))
      index = index + 1
  return cutup

def stitchTogether(cutImg, w, h):
  dim = cutImg[0].shape
  w_i, h_i = dim[0], dim[1]
  n = len(cutImg)

  rangeW = w // w_i
  rangeH = h // h_i

  img_lst = []

  cnt = 0
  for j in range(0, rangeH):
    lst = []
    for i in range(0, rangeW):
      if cnt >= n:
         return cv2.vconcat(img_lst)
      lst.append(cutImg[cnt])
      cnt += 1
    img_lst.append(cv2.hconcat(lst))



  return cv2.vconcat(img_lst)