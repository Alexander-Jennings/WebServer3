#!/usr/bin/env python
import os
import socket
from webob import Response

def get_path(httpRequest):
	try:
		path = httpRequest.split()[1]
		print('extracted this path: ' + path)
		return path
	except IndexError:
		return "/notavalidpath"
	
	
def get_file_contents(path):
	"""Returns the contents of the specified file as a string. Path should include the name of the file."""
	file = open(path)
	contents = file.read()
	file.close()
	return contents
	
def compute_content_type(path):
	"""Returns the content type associated with file with the given path"""
	suffix = path[path.find('.')+1:]
	if suffix == 'txt':
		return 'text/plain'
	elif suffix == 'jpg':
		return 'image/jpeg'
	elif suffix == 'png':
		return 'image/png'
	elif suffix == 'js':
		return 'text/javascript'
	elif suffix == 'css':
		return 'text/css'
	elif suffix == 'gif':
		return 'image/gif'
	else:
		return 'text/html'
	
def main():
	doc_root = 'content'
	doc_index = '/index.html'
	site_index = doc_root + '/site_index.html'
	file_not_found_page = doc_root + '/no_such_file.html'
	
	valid_paths = ['/', '/index.html', '/books/tomsawyer.txt', '/books/theimportanceofbeingearnest.txt', '/pictures/puppy.jpg', '/pictures/catfight.jpg']
	
	directories = ['pictures', 'books']
	
	redirects = {}
	redirects['/home'] = doc_index
	redirects['/index'] = doc_index
	redirects['/'] = doc_index
	redirects['/puppy'] = '/pictures/puppy.jpg'
	redirects['/cat'] = '/pictures/catfight.jpg'
	redirects['/tomsawyer'] = '/books/tomsawyer.txt'
	redirects['/earnest'] = '/books/theimportanceofbeingearnest.txt'
	
	# list of urls to ignore - do not try to serve anything 
	url_ignore_list = ['/favicon.ico', '']
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(('',8080))
	sock.listen(5)
	
	while True:
		conn, client_address = sock.accept()
		request = conn.recv(1024).decode('utf-8')
		print('received "%s"'% (request)) 
		
		res = Response()
		
		path = get_path(request)
		
		body = ''
		
		if path not in url_ignore_list:
			#redirect to valid document
			if path in redirects:
				res.status_code = 302
				res.location = redirects[path]
				res.content_type = ''
				res.content_length = ''
					#requested a directory
			elif path[1:] in directories:
				body = get_file_contents(site_index)
			#requested a valid document
			elif path in valid_paths:
				path = doc_root + path
				body = get_file_contents(path)
				res.content_type = compute_content_type(path)
				res.status_code = 200

			#don't have the requested file
			else:
				res.status_code = 404
				body = get_file_contents(file_not_found_page)
				
			
			if path not in redirects:
				res.text = body
				
			res.headers['Connection'] = 'close'
			conn.send('HTTP/1.1 '.encode('utf-8') + str(res).encode('utf-8'))
			conn.close()


if __name__ == '__main__':
	main()