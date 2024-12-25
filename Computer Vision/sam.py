import numpy as np
import pandas as pd
import argparse
import cv2
import os
import time
import requests
import matplotlib.pyplot as plt
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry,SamPredictor

sam_checkpoint = "model/sam_vit_h_4b8939.pth"
device = "cpu"
model_type = "default"

sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)
predictor = SamPredictor(sam)

print("Model Loaded")

image = cv2.imread('dog_cat.jpg')
print(predictor.set_image(image))

input_point = np.array([[800, 450]])
input_label = np.array([1])

print("Working on Predication")

masks, scores, logits = predictor.predict(
    point_coords=input_point,
    point_labels=input_label,
    multimask_output=True,
)

print(masks.shape,scores, logits)

