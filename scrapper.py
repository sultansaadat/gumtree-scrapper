import requests
import re
import csv

import thread
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)"
REQUEST_HEADERS = {'User-agent': USER_AGENT,}

class SearchListing:

    website = "http://www.gumtree.co.za"
    parsedURLS = []
    urlList = []
    tel_082 = []
    tel_0818 = []
    tel_0810 = []
    tel_083 = []
    tel_084 = []
    tel_others = []

    def __init__(self):
        self.category = ""
        self.query = ""    
        self.location = ""

    def __str__(self):
        return "Search listing"

    def grabURLs(self, from_page, to_page):
        currentPageNumber = 0
        totalPages  = 0
        for x in range(from_page, to_page): 
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
            # ul = divs[0].ul[1]        # first ul is of top ads but we need the second one i.e. paged ul
            # for li in ul.li:
            #   title = li.find_all("div", class_="title")
            #   print title.a.get("href")

    def grabPhones(self):
        for url in self.urlList:
            if not url in self.parsedURLS:
                self.parsedURLS.append(url);
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
        self.saveToCSV("vodacom_082", self.tel_082)
        self.saveToCSV("mtn_083", self.tel_083)
        self.saveToCSV("cell_c_084", self.tel_084)
        self.saveToCSV("vodacom_0818", self.tel_0818)
        self.saveToCSV("mtn_0810", self.tel_0810)
        self.saveToCSV("others", self.tel_others)
        print "Finished"
    
    def appendTelephone(self, tel):
        tel = tel.replace("(", "").replace(")", "").replace(" ", "")
        extention = tel[:3]
        extention2 = tel[:4]

        if  tel in self.tel_082 or  tel in self.tel_083 or  tel in self.tel_084 or tel in self.tel_0818 or tel in self.tel_others:
             print ". " ,
        elif extention == "082" and not tel in self.tel_082:
            self.tel_082.append(tel)
            print "* " ,
            # print "082 => " + tel + " ext: " + extention + ", ext2: " + extention2
        elif extention == "083" and not tel in self.tel_083:
            self.tel_083.append(tel)
            print "* " ,
            # print "083 => " + tel + " ext: " + extention + ", ext2: " + extention2
        elif extention == "084" and not tel in self.tel_084:
            self.tel_084.append(tel)
            print "* " ,
            # print "084 => " + tel + " ext: " + extention + ", ext2: " + extention2
        elif extention2 == "0818" and not tel in self.tel_0818:
            self.tel_0818.append(tel)
            print "* " ,
            # print "0818 => " + tel + " ext: " + extention + ", ext2: " + extention2
        elif extention2 == "0810" and not tel in self.tel_0810:
            self.tel_0810.append(tel)
            print "* " ,
            # print "0810 => " + tel + " ext: " + extention + ", ext2: " + extention2
        else:
            self.tel_others.append(tel)
            print "* " ,
            # print "others => " + tel + " ext: " + extention + ", ext2: " + extention2
            
    def saveToCSV(self, filename, tel_list):
        for tel in tel_list:
            self.append_csv(filename, tel)
        # with open(filename + '.csv', 'wb') as csvfile:
           #  fieldnames = ['telephone']
           #  writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
           #  writer.writeheader()
           #  for tel in tel_list:
           #    writer.writerow({'telephone': str(tel)})

    def create_csv(self, filename):
        with open(filename + '.csv', 'wb') as csvfile:
            fieldnames = ['telephone']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    def append_csv(self, filename, telephone):
        with open(filename + '.csv', 'ab') as csvfile:
            fieldnames = ['telephone']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'telephone': str(telephone)})
    def load_csv(self, filename, tel_list):
        with open(filename + '.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                tel_list.append(row["telephone"])
        return tel_list
        


test = SearchListing()

# test.create_csv("vodacom_082")
# test.create_csv("vodacom_0818")
# test.create_csv("mtn_083")
# test.create_csv("mtn_0810")
# test.create_csv("cell_c_084")
# test.create_csv("others")

test.tel_082 = test.load_csv("vodacom_082", test.tel_082)
test.tel_0818 = test.load_csv("vodacom_0818", test.tel_0818)
test.tel_083 = test.load_csv("mtn_083", test.tel_083)
test.tel_0810 = test.load_csv("mtn_0810", test.tel_0810)
test.tel_084 = test.load_csv("cell_c_084", test.tel_084)
test.tel_others = test.load_csv("others", test.tel_others)

# print test.tel_others

def scrapPages(test, fromIdx, toIdx):
    test.urlList = []
    test.tel_082 = []
    test.tel_083 = []
    test.tel_084 = []
    test.tel_0818 = []
    test.tel_0810 = []
    test.tel_others = []
    result = test.grabURLs(fromIdx,toIdx)
    test.grabPhones()
    test.generateCSVs()
    print "Processed "+ str(fromIdx) + " => " + str(toIdx)
    
        
for x in xrange(5705, 20000):
    scrapPages(test, x,x+1)
# scrapPages(test, 2,4)
# scrapPages(test, 4,6)
# scrapPages(test, 6,8)
# scrapPages(test, 8,10)
# scrapPages(test, 10,12)


