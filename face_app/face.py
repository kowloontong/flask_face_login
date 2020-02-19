# import the necessary packages
import numpy as np
import argparse
#import imutils
import pickle
import time
import cv2
import os
import sklearn

class Face_app():
	def __init__(self):
		# load our serialized face detector from disk
		self.protoPath = "./face_app/face_detection_model/deploy.prototxt"
		self.modelPath = "./face_app/face_detection_model/res10_300x300_ssd_iter_140000.caffemodel"
		self.detector = cv2.dnn.readNetFromCaffe(self.protoPath, self.modelPath)
		# load our serialized face embedding model from disk
		self.embedder = cv2.dnn.readNetFromTorch('./face_app/openface_nn4.small2.v1.t7')
		# load the actual face recognition model along with the label encoder
		self.recognizer = pickle.loads(open('./face_app/output/recognizer.pickle', "rb").read())
		self.le = pickle.loads(open('./face_app/output/le.pickle', "rb").read())

	def recognize_fromImg(self,frame):
		(h, w) = frame.shape[:2]
		# construct a blob from the image
		imageBlob = cv2.dnn.blobFromImage(
			cv2.resize(frame, (300, 300)), 1.0, (300, 300),
			(104.0, 177.0, 123.0), swapRB=False, crop=False)
		# apply OpenCV's deep learning-based face detector to localize
		# faces in the input image
		self.detector.setInput(imageBlob)
		detections = self.detector.forward()
		# loop over the detections
		name_list = []
		for i in range(0, detections.shape[2]):
			# extract the confidence (i.e., probability) associated with
			# the prediction
			confidence = detections[0, 0, i, 2]
			# filter out weak detections
			if confidence > 0.5:
				# compute the (x, y)-coordinates of the bounding box for
				# the face
				box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
				(startX, startY, endX, endY) = box.astype("int")
				# extract the face ROI
				face = frame[startY:endY, startX:endX]
				(fH, fW) = face.shape[:2]
				# ensure the face width and height are sufficiently large
				if fW < 20 or fH < 20:
					continue
				# construct a blob for the face ROI, then pass the blob
				# through our face embedding model to obtain the 128-d
				# quantification of the face
				faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,
					(96, 96), (0, 0, 0), swapRB=True, crop=False)
				self.embedder.setInput(faceBlob)
				vec = self.embedder.forward()
				# perform classification to recognize the face
				preds = self.recognizer.predict_proba(vec)[0]
				j = np.argmax(preds)
				proba = preds[j]
				name = self.le.classes_[j]
				# draw the bounding box of the face along with the
				# associated probability
				text = "{}: {:.2f}%".format(name, proba * 100)
				print(text)
				name_list.append(name)
		return name_list
				
		
