import urllib2, urllib
import re
import thread
import time, os, shutil
import linecache

# ---------------------------------------------------------------------------
# this program is for collecting images of products that are searched in
# Tennis Express, user need to enter the search keywords to run the program
# Program Name: Tennis Express Net Spider
# Version: 0.2
# Author: Gerry.Z
# Time: 2017-02-14
# Usage: run this code in terminal, and type in product you wants to search
# Output: a folder contains inform of all products from search result
# ---------------------------------------------------------------------------

class NetSpider:
    def __init__(self):
        self.page = 1
        self.pages = []
        self.enable = False
        self.search_key_word = None
        self.search_result_page_code_txt = 'page_code.txt'
        self.search_result_page_code_html = 'page_code.html'
        self.image_size = None


    def searchKeyWordTrans(self, inputStr):
        # check if input string is empty
        if (len(inputStr) == 0):
            print 'Error, keyword cannot be empty!'
            outputStr = None
        else:
            # if not, change the space to dash sigh
            spaceCompressRe = re.compile(r'\ +')
            inputStr = (spaceCompressRe.subn(' ', inputStr)[0]).lower()
            print 'Now searching for : ', inputStr
            outputStr = inputStr.replace(' ', '-')
            self.search_key_word = outputStr
        return outputStr


    def getPage(self, keyword):
        myUrl = 'https://www.tennisexpress.com/all-products/browse/keyword/' + keyword
        #user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36'+\
                     ' (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        headers = {'User-Agent': user_agent}
        req = urllib2.Request(myUrl, headers=headers)
        myResponse = urllib2.urlopen(req)
        myPage = myResponse.read()

        # write code in html file
        page_code_file_html = open(self.search_result_page_code_html, 'w')
        page_code_file_html.write(myPage)
        page_code_file_html.close()

        # write code in txt file
        page_code_file = open(self.search_result_page_code_txt, 'w')
        page_code_file.write(myPage)
        page_code_file.close()


    def exploreWeb(self, keyword):

        # check file search_result_page_code_txt line by line
        # if the searching result have more than one page, change the url
        matchTest = None
        matchTestPos = 1
        with open(self.search_result_page_code_txt) as f:
            lines = f.readlines()
            for line in lines:
                matchTest = re.match('.*?<div class="pagethru2">\s', str(line))
                if (matchTest):
                    break
                else:
                    matchTestPos += 1

        if (matchTest):
            print 'Several pages are in the searching result, postion:', matchTest.endpos,\
                ' page: ', matchTestPos
            # extract the link out of the page
            line = linecache.getline(self.search_result_page_code_txt, matchTestPos+1)
            viewAllLink = re.compile(r'\"+').split(str(line))[1]
            print 'Now reload viewall page: ', viewAllLink
            viewAllLinkKeywordArray = re.compile(r'/+').split(viewAllLink)
            priviewAllLinkKeyword = viewAllLinkKeywordArray[-3] + '/' + viewAllLinkKeywordArray[-2] + \
                                    '/' + viewAllLinkKeywordArray[-1]
            # reload this page
            self.getPage(priviewAllLinkKeyword)
            print 'Reload finish'
        else:
            print 'Only one page is in the searching result, don\'t need redirect'

        # put all products link into an array
        searchResultProductsLinkList = []
        with open(self.search_result_page_code_txt) as f:
            lines = f.readlines()
            for line in lines:
                matchTest = re.match('<a class=\"product\".*?', str(line))
                if (matchTest != None):
                    searchResultProductsLink = re.compile(r'\"+').split(str(line))[3]
                    searchResultProductsLinkList.append(searchResultProductsLink)

        # build a file for store searching result
        print 'All result products are listed here: '
        for productsLink in searchResultProductsLinkList:
            print productsLink

        # create new home folder
        print 'Create a folder and store all products information'
        searchResultHomeFolderPath = 'tennisExpress_search_result_' + keyword
        if not os.path.exists(searchResultHomeFolderPath):
            os.makedirs(searchResultHomeFolderPath)

        # in the home folder, create sub-folders for all products
        # empty the home folder first
        for the_file in os.listdir(searchResultHomeFolderPath):
            file_path = os.path.join(searchResultHomeFolderPath, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)

        for productsLink in searchResultProductsLinkList:
            # create every sub folder based on the products name
            productsName = productsLink.split('/')[-1]
            productsNamePath = searchResultHomeFolderPath + '/' + productsName
            if not os.path.exists(productsNamePath):
                os.makedirs(productsNamePath)

            # create a file to store the link
            product_link_file = open(productsNamePath + '/pageLink.txt', 'w')
            product_link_file.write(productsLink)
            product_link_file.close()

            # create files to store the page source code
            page_file_name = productsNamePath + '/page_' + productsName
            self.savePageInFolder(productsLink, page_file_name)

        print 'All products source pages are successfully saved'
        # return the link list and home folder, for other method to use
        return (searchResultHomeFolderPath, searchResultProductsLinkList)


    def savePageInFolder(self, link, fileName):
        myUrl = link
        # user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36' + \
                     ' (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        headers = {'User-Agent': user_agent}
        req = urllib2.Request(myUrl, headers=headers)
        myResponse = urllib2.urlopen(req)
        myPage = myResponse.read()
        # write code in html and txt file
        page_code_file_html = open(fileName + '.html', 'w')
        page_code_file_html.write(myPage)
        page_code_file_html.close()

        page_code_file_txt = open(fileName + '.txt', 'w')
        page_code_file_txt.write(myPage)
        page_code_file_txt.close()


    def getProductsImg(self, homeFolderPath, productsLinkList):
        # this method is used to collecting all products image from the source web code
        # first check the image size
        if not (self.image_size):
            size = 100
        else:
            size = self.image_size

        for productsLink in productsLinkList:
            # create a folder to store image
            productsName = productsLink.split('/')[-1]
            productsNamePath = homeFolderPath + '/' + productsName
            productsImgPath = productsNamePath + '/' + productsName + '_img'
            if not os.path.exists(productsImgPath):
                os.makedirs(productsImgPath)

            # scan source code to find products image
            pageFileName = productsNamePath + '/page_' + productsName + '.txt'

            productsImgLinkList = []
            with open(pageFileName) as pgf:
                lines = pgf.readlines()
                for line in lines:
                    matchTest = re.match('.*?<a id=\"zoomer\".*?|.*?<a class=\"altImage\".*?', str(line))
                    if (matchTest != None):
                        productsImgLink = re.compile(r'\"+').split(str(line))[3]
                        productsImgLinkList.append(productsImgLink)
                        #print productsImgLink

            # put these source in a txt file and download them
            productsImgLinkFile = open(productsImgPath + '/' + productsName + '_imgLinks.txt', 'w')
            productsImgLinkFile.write('imageLinks\n')
            productsImgLinkFile.close()

            productsImgLinkFile = open(productsImgPath + '/' + productsName + '_imgLinks.txt', 'a')
            for productsImgLink in productsImgLinkList:
                # write link in a txt file

                productsImgLinkFile.write(productsImgLink + '\n')
                # download images
                imgFileName = productsImgPath + '/' + productsImgLink.split('/')[-1]

                try:
                    if not os.path.exists(imgFileName):
                        urllib.urlretrieve(productsImgLink, imgFileName)
                    else:
                        continue
                except Exception as e:
                    print(e)
                    continue
                # print productsImgLink
                # print imgFileName

            productsImgLinkFile.close()


    def start(self, inputStr):
        self.enable = True
        keyword = self.searchKeyWordTrans(inputStr)
        if keyword:
            self.getPage(keyword)
            print 'Page file saved'
            # get the home path and all products link list
            (homeFolderPath, productsLinkList) = self.exploreWeb(keyword)

            # get images of all products
            self.getProductsImg(homeFolderPath, productsLinkList)

            print 'Program finish'
        else:
            print 'Input error, please try again'


print u"""
---------------------------------------
    Name:     Net Spider TennisExpress
    Version:  0.2
    Author:   Gerry.Z
    Language: Python 2.7
---------------------------------------
"""

inputStr = raw_input("Enter keyword you want to search: ")
mySpider = NetSpider()
mySpider.start(inputStr)
