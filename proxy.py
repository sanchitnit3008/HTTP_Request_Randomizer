import os
import sys

from flask import Flask
from flask import request
# from project.http.requests.proxy.requestProxy import requestProxy
from project.http.requests.parsers.freeproxyParser import freeproxyParser
from project.http.requests.parsers.proxyforeuParser import proxyforeuParser
from project.http.requests.parsers.rebroweeblyParser import rebroweeblyParser
from project.http.requests.parsers.samairproxyParser import semairproxyParser
from project.http.requests.useragent.userAgent import UserAgentManager
import requests
from requests.exceptions import ConnectionError
import random
import time
from requests.exceptions import ReadTimeout
application = Flask(__name__)

__author__ = 'pgaref'

class RequestProxy:
		def __init__(self, web_proxy_list=[],proxy_file=os.path.join(os.path.dirname(__file__), './project/http/requests/data/proxy_list.txt')):
				self.userAgent = UserAgentManager();
				self.proxy_file = proxy_file
				self.proxy_list = self.load_proxy_list(self.proxy_file)

		def get_proxy_list(self):
				return self.proxy_list

		def load_proxy_list(self, proxyfile):
				"""
				useragentfile : string
						path to text file of user agents, one per line
				"""
				proxy_list = []
				with open(proxyfile, 'rb') as uaf:
						for ua in uaf.readlines():
								if ua:
										proxy_list.append(ua.rstrip())
				return proxy_list


		def generate_random_request_headers(self):
				headers = {
						"Connection": "close",  # another way to cover tracks
						"User-Agent": self.userAgent.get_random_user_agent()
				}  # select a random user agent
				return headers

		#####
		# Proxy format:
		# http://<USERNAME>:<PASSWORD>@<IP-ADDR>:<PORT>
		#####
		def generate_proxied_request(self, url, params={}, req_timeout=5):
				try:
						random.shuffle(self.proxy_list)
						req_headers = dict(params.items() + self.generate_random_request_headers().items())

						rand_proxy = random.choice(self.proxy_list)
						print "Using proxy: {0}".format(str(rand_proxy))
						request = requests.get(url, proxies={"http": rand_proxy},
																	 headers=req_headers, timeout=req_timeout)
						return request
				except ConnectionError:
						try:
								self.proxy_list.remove(rand_proxy)
						except ValueError:
								pass
						print "Proxy unreachable - Removed Straggling proxy: {0} PL Size = {1}".format(rand_proxy,
																																													 len(self.proxy_list))
				except ReadTimeout:
						try:
								self.proxy_list.remove(rand_proxy)
						except ValueError:
								pass
						print "Read timed out - Removed Straggling proxy: {0} PL Size = {1}".format(rand_proxy,
																																												len(self.proxy_list))
@application.route('/',methods=['GET'])
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"


@application.route('/refreshProxies',methods=['GET','POST'])
def refreshProxies():
	#####
	# Each of the classes below implements a specific URL Parser
	#####
	parsers = []
	parsers.append(freeproxyParser('http://free-proxy-list.net'))
	parsers.append(proxyforeuParser('http://proxyfor.eu/geo.php', 100.0))
	parsers.append(rebroweeblyParser('http://rebro.weebly.com/proxy-list.html'))
	parsers.append(semairproxyParser('http://www.samair.ru/proxy/time-01.htm'))

	print "=== Initialized Proxy Parsers ==="
	for i in range(len(parsers)):
			print "\t {0}".format(parsers[i].__str__())
	print "================================="

	proxy_list = []
	for i in range(len(parsers)):
			proxy_list += parsers[i].parse_proxyList()
	thefile = open(os.path.join(os.path.dirname(__file__), './project/http/requests/data/proxy_list.txt'), 'w')
	for item in proxy_list:
		thefile.write("%s\n" % item)
	return 'Done writing'

@application.route('/testIP',methods=['GET'])
def testIP(params={}, req_timeout=5);
	url = request.args.get('url')
	req_proxy = RequestProxy();
	firstTime = time.time()
	start = time.time()
	proxy = request.args.get('proxy')
	req_headers = dict(params.items() + req_proxy.generate_random_request_headers().items())
	request = requests.get(url, proxies={"http": proxy},
										headers=req_headers, timeout=req_timeout)
	return request.text

@application.route('/fetchHTML', methods=['GET'])
def fetchHTML():
	url = request.args.get('url')
	firstTime = time.time()
	start = time.time()
	req_proxy = RequestProxy();
	print "Initialization took: {0} sec".format((time.time() - start))
	requestInside = None
	while requestInside is None:
		start = time.time()
		requestInside = req_proxy.generate_proxied_request(url)
		print "Proxied Request Took: {0} sec => Status: {1}".format((time.time() - start), requestInside.__str__())
	print "Total time to fetch: {0} sec".format((time.time() - firstTime))
	return requestInside.text


if __name__ == "__main__":
		application.run(host='0.0.0.0')