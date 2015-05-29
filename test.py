import os

def check_files():
	if 'ie_numbers.txt' in os.listdir('data'):
		print 'Yay!'

def write_status(id_number):
	status = open('data/%s.status' % id_number, 'a')
	status.close()

def test_range():
	no_of_uploads = raw_input('> ')
	for i in range(1, no_of_uploads):
		print i

#write_status('50004')

def strip_url():
	with open('data/addtoflickrcommons.txt') as read_file:
		for line in read_file:
			line = line[-9:]
			with open('data/commonsnumbers.txt', 'a') as write_file:
				write_file.write(line)
				write_file.close()
	read_file.close()

#strip_url()

def print_keys():
	print os.environ['DNZ_API_KEY']
	print os.environ['FLICKR_API_KEY']
	print os.environ['FLICKR_SECRET']

print_keys()