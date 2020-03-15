import numpy as np

def degToTick(deg):
	return int(np.round(deg*4095/360))

def tickToDeg(tick):
	return tick/4095*360


def main():
	print("dynamixel_utils")

if __name__ == '__main__':
	main()