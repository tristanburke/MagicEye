import cv2
import math
import random
import os
import time


image_dir = "/Users/tristanburke/Desktop/Desktop Stuff/Code/MagicEye/images/angle/"
FRAME_W = 540					# Frame width of the face capture - short/wide is preferred (the smaller the faster but less the accurate)
FRAME_H = 540					# Frame height
x_rotations = []				# All the X rotations within the image set
z_rotations = []				# All the Z rotations within the image set
x_previous_rotation = 0 		# X rotation of the previous image
z_previous_rotation = 0 		# Z rotation of the previous image
previous_face_x = 0 			# X location of the last seen face
previous_face_y = 0 			# Y location of the last seen face 
movement_speed = 0.1			# Max radians to move per frame


# Given a list of numbers and a target number, find the closest number in the list to the target
def find_closest_number(numbers, target):
    return min(numbers, key=lambda x: abs(x - target))


# Given two numbers and a speed, interpolate a coordinate between them
def interpolate_angle(previous, target):
	difference = abs(previous - target)
	if difference < movement_speed:
		return target
	else:
		if target < previous:
			return previous - movement_speed
		else:
			return previous + movement_speed


# Parse the images within the image folder 
def parse_image_folder():
	# Iterate through the file names and parse out the x and z rotations
	global x_rotations
	global z_rotations
	for file in os.listdir(image_dir):
		if "_" in file:
			x_rotations += [float(file.split("_")[0])]
			z_rotations += [float(file.split("_")[1].replace(".png", ""))]
	print(len(x_rotations))


# Return an image in the direction of 0, 0 rotation
def move_back_to_center():
	# Calculate the distance between
	global x_previous_rotation
	global z_previous_rotation
	x_target_rotation = interpolate_angle(previous=x_previous_rotation, target=0)
	z_target_rotation = interpolate_angle(previous=z_previous_rotation, target=0)

	# Find the closest image rotation to the target rotation
	x_image_rotation = find_closest_number(x_rotations, x_target_rotation)
	z_image_rotation = find_closest_number(z_rotations, z_target_rotation)

	# Update previous rotation values
	x_previous_rotation = x_target_rotation
	z_previous_rotation = z_target_rotation

	return image_dir + str(x_image_rotation) + "_" + str(z_image_rotation) + ".png"


# Return an image in the direction of the target x, y, and distance
def move_to_face(x, y, distance):
	# Calculate x and z rotation
	x_face_rotation = math.atan(y / distance)
	z_face_rotation = math.atan(x / distance)

	# Calculate the distance between
	global x_previous_rotation
	global z_previous_rotation
	x_target_rotation = interpolate_angle(previous=x_previous_rotation, target=x_face_rotation)
	z_target_rotation = interpolate_angle(previous=z_previous_rotation, target=z_face_rotation)

	# Find the closest image rotation to the target rotation
	x_image_rotation = find_closest_number(x_rotations, x_target_rotation)
	z_image_rotation = find_closest_number(z_rotations, z_target_rotation)

	# Update previous rotation values
	x_previous_rotation = x_target_rotation
	z_previous_rotation = z_target_rotation

	return image_dir + str(x_image_rotation) + "_" + str(z_image_rotation) + ".png"


# Pick a single face to focus on and calculate distance
def parse_faces(faces):
	global previous_face_x
	global previous_face_y
	minimum_distance = 100000000 # whatever
	face_index = 0

	# Pick the face closest to the angle the eye is pointing
	for index in range(len(faces)):
		x, y, w, h = faces[index]
		distance = ((x - previous_face_x)**2 - (y - previous_face_y)**2)**0.5
		if distance < minimum_distance:
			face_index = index
			minimum_distance = distance
	return faces[face_index]


# Given a width and height of a face detection, estimate how far the face is from the camera
def calculate_distance(w, h):
	return 200


# Return a random x,y point and distance
def random_point():
	return [int(random.randint(0,FRAME_W) - (FRAME_W / 2)), int(random.randint(0,FRAME_H) - (FRAME_H / 2)), 200]


# Main function that detects faces and displays the eye images
def main():

	# Parse the images in the specified folder
	parse_image_folder()

	# Set the cv2 display window to full screen
	# cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
	# cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
	window_height, window_width = 1600, 2560


	# TEMP DELETE LATER
	counter = 0
	point = random_point()
	while True:

		# TEMP DELETE LATER
		if counter == 60:
			counter = 0
			point = random_point()


		image = cv2.imread(image_dir + "0.0_0.0.png")	# Default image to display	
		faces = []
		if len(faces) >= 0:

			# If faces have been detected, pick a face to point towards and store it's x,y poistion and width, height
			# x, y, w, h = parse_faces(faces)
			# distance = calculate_distance(w, h)

			# Given a target face, pick an eye image to display
			# image_path = move_to_face(x, y, distance)
			image_path = move_to_face(point[0], point[1], point[2])
			image = cv2.imread(image_path)
			x, y = int(point[0] + (FRAME_W / 2)), int(point[1] + (FRAME_H / 2))
			cv2.rectangle(image, (x, y), (x + 3, y + 3), (0, 255, 0), 4)
		else:
			# If no face has been detected, move back towards the center
			image_path = move_back_to_center()
			image = cv2.imread(image_path)

		# Pad the image with a black border to center it
		w,h,c = image.shape
		padded_height, padded_width = int((window_height - h) / 2), int((window_width - w) / 2)
		# image = cv2.copyMakeBorder(image, padded_height, padded_height, padded_width, padded_width, 0)
		cv2.imshow('window', image)

	    # If you type q at any point this will end the loop and thus end the code.
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
		counter += 1

	# When everything is done, release the capture information and stop everything
	cv2.destroyAllWindows()

if __name__ == "__main__":
	main()
