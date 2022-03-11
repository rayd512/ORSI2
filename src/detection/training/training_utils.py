import os

# source: https://github.com/learncodebygaming/opencv_tutorials/blob/master/008_cascade_classifier/cascadeutils.py
def generate_negative_description_file():
	path = 'resized_negative'
	with open('neg.txt', 'w') as f:
		for filename in os.listdir(path):
			f.write(path + '/' + filename + '\n')