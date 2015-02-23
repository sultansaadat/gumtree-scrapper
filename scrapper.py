import requests
import re
import csv

import thread
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)"
REQUEST_HEADERS = {'User-agent': USER_AGENT,}

class SearchListing:

    website = "http://www.gumtree.co.za"
    urlList = []
    tel_082 = []
    tel_0818 = []
    tel_0810 = []
    tel_083 = []
    tel_084 = []
    tel_others = []

    def __init__(self, category, query="", location=""):
        self.category = category
        self.query = query    
        self.location = location

    def __str__(self):
        return "Search listing"

    def grabURLs(self):
    	currentPageNumber = 0
    	totalPages  = 0
    	
    	baseURL = "http://www.gumtree.co.za/s-all-the-ads/v1b0p1"
    	request = requests.get(baseURL, headers=REQUEST_HEADERS)
    	if request.status_code == 200:
    		souped = BeautifulSoup(request.text, "html5lib")
    		pagination = souped.find_all("p", class_="pagination-results-count")
    		if len(pagination) > 0:
    			paginationString = pagination[0]
    			totalPages = int(paginationString.span.string.split(' ')[5].replace(',', ''))
    			print totalPages
    		self.parsePage(souped)

    	if totalPages > 0:
    		# first page is already indexed above and page index on gumTree is not zero based index
    		for x in range(2,totalPages+2): 
    			print "parsing Page#: " + str(x)
    			URL = "http://www.gumtree.co.za/s-all-the-ads/page-%i/v1b0p1" % x 
    			# print URL
    			request = requests.get(URL, headers=REQUEST_HEADERS)
    			if request.status_code == 200:
    				souped = BeautifulSoup(request.text, "html5lib")
    				self.parsePage(souped)
    	return self.urlList

    def parsePage(self, souped):
    	divs = souped.find_all("div", class_="view")
    	if len(divs) > 1:
    		hyperlinks = divs[1].find_all("a", class_="href-link")
    		for x in hyperlinks:
    			self.urlList.append(self.website + x.get("href"))
    		# ul = divs[0].ul[1]		# first ul is of top ads but we need the second one i.e. paged ul
    		# for li in ul.li:
    		# 	title = li.find_all("div", class_="title")
    		# 	print title.a.get("href")

    def grabPhones(self):
    	for url in self.urlList:
    		request = requests.get(url, headers=REQUEST_HEADERS)
    		if request.status_code == 200:
    			souped = BeautifulSoup(request.text, "html5lib")
    			telephone = souped.find_all("a", class_="telephone")
    			if len(telephone) > 0:
    				href = telephone[0].get("href")
    				telephone = href[4:]
    				self.appendTelephone(telephone)
    					# print "telephones Size: " + str(len(self.telephones)) + " curr: " + href[4:] + " original:" + href
    	
    def generateCSVs(self):
    	self.saveToCSV("telephones_082", self.tel_082)
    	self.saveToCSV("telephones_083", self.tel_083)
    	self.saveToCSV("telephones_084", self.tel_084)
    	self.saveToCSV("telephones_0818", self.tel_0818)
    	self.saveToCSV("telephones_0810", self.tel_0810)
    	self.saveToCSV("telephones_others", self.tel_others)
    	print "Finished"
	
    def appendTelephone(self, tel):
    	tel = tel.replace("(", "").replace(")", "").replace(" ", "")
    	extention = tel[:3]
    	extention2 = tel[:4]

    	if  tel in self.tel_082 or  tel in self.tel_083 or  tel in self.tel_084 or tel in self.tel_0818 or tel in self.tel_0810:
    		 print tel + " already exist" 
    	elif extention == "082" and not tel in self.tel_082:
    		self.tel_082.append(tel)
    		# print "082 => " + tel + " ext: " + extention + ", ext2: " + extention2
    	elif extention == "083" and not tel in self.tel_083:
    		self.tel_083.append(tel)
    		# print "083 => " + tel + " ext: " + extention + ", ext2: " + extention2
    	elif extention == "084" and not tel in self.tel_084:
    		self.tel_084.append(tel)
    		# print "084 => " + tel + " ext: " + extention + ", ext2: " + extention2
    	elif extention2 == "0818" and not tel in self.tel_0818:
    		self.tel_0818.append(tel)
    		# print "0818 => " + tel + " ext: " + extention + ", ext2: " + extention2
    	elif extention2 == "0810" and not tel in self.tel_0810:
    		self.tel_0810.append(tel)
    		# print "0810 => " + tel + " ext: " + extention + ", ext2: " + extention2
    	else:
    		self.tel_others.append(tel)
    		# print "others => " + tel + " ext: " + extention + ", ext2: " + extention2
            
    def saveToCSV(self, filename, tel_list):
    	
    	with open(filename + '.csv', 'wb') as csvfile:
		    fieldnames = ['telephone']
		    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		    writer.writeheader()
		    for tel in tel_list:
		    	writer.writerow({'telephone': str(tel)})

	# def saveToCSV(self, filename, tel_list):
	# 	print "hello"
		


test = SearchListing("Audi")
result = test.grabURLs()
test.grabPhones()
test.generateCSVs()
# print "result Length: " + str(len(result))