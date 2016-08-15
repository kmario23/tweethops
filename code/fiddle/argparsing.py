import argparse
import sys
import os

if __name__ == '__main__':
	"""An example to demonstrate how argparse module works"""

	parser = argparse.ArgumentParser()
	requiredArgs = parser.add_argument_group('must need arguments')
	requiredArgs.add_argument('-o', '--output', help='Output txt file to write tweets', required=True)
	args = parser.parse_args()

	filepath = os.getcwd() + os.path.sep + args.output
	if os.path.exists(filepath):
		sys.exit("output file already exists; Give new filename!")
	else:
		fi = open(args.output,'a')
		sys.exit("{} was successfully created".format(args.output))