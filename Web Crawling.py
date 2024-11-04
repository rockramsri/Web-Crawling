from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urlparse,urlunparse
import time
from datetime import datetime
from collections import deque
import heapq
import random

# Global Variables
cssFileCount=0
jssFileCount=0
pngFileCount=0
svgFileCount=0
exceptionCountFor404=0
exceptionCountFor403=0
totalSizeOfCrawledData=0
exceptionlist=[] # This is for debugging
innerExceptionList=[] # Second exception list for another debugging state
startTime=time.time() # Temporary timer to stop the crawler, checking the duration for each iteration of crawling
totalcrawls=0 # Stores the total number of crawls
urlQueue=[] # Helps track if the domain is already in the queue
seen_domains=set() # Helps track if the URL is already in the queue
seen_urls=set()
robot_txt_disallowed_urls=set() # will store the directories with parent to check
class customQueue:
    url=None
    urlDepth=0
    def __init__(self,url,urlDepth) -> None:
        self.url=url
        self.urlDepth=urlDepth
    def __lt__(self,other):     # if the priorities are same then heapmap will sort based on the length
        return len(self.url) < len(other.url)

# Converts a relative URL to an absolute URL using the parent URL
def get_Absoulte_path(parentUrl,urlString):
    parsedURL=urlparse(urlString)
    parsedParentUrl=urlparse(parentUrl)
    #print(parsedURL)
    if not all([parsedURL.netloc,parsedURL.scheme]) and parsedURL.path!=None and len(parsedURL.path)!=0:
            parsedURL=parsedURL._replace(scheme=parsedParentUrl.scheme,netloc=parsedParentUrl.netloc)
            #print(urlunparse(parsedURL)+" : "+urlString)
            return  str(urlunparse(parsedURL))
    return urlString

# Parses the domain from the raw URL (up to 2 values separated by a dot), excluding port numbers if present
def get_Parsed_Domain(urlString):
    parsedURL=urlparse(urlString)
    domain=parsedURL.netloc
    subdomainList=domain.split(".")
    if len(subdomainList)>=2:
        if ":" in subdomainList[1]:
            return subdomainList[0]+subdomainList[1][:subdomainList[1].index(":")]
        else:
            return ".".join(subdomainList[:2])
    return ".".join(subdomainList)

# Checks if the raw URL has already been processed
def check_if_the_url_already_in_queue(url):
    if url in seen_urls:
        return True
    return False
# Returns priority based on whether it's a new domain or not
def check_if_the_domain_already_in_queue_and_get_priority(url):
    if get_Parsed_Domain(url) in seen_domains:
        return 2
    return 1

# Parses and verifies the URL, and counts the number of .css, .js, .png, and .svg files
def parseAndvalidateURL(urlString):
    parsedURL=urlparse(urlString)
    if all([parsedURL.netloc,parsedURL.scheme]) and parsedURL.netloc[len(parsedURL.netloc)-3:] == ".nz":
        if parsedURL.path[len(parsedURL.path)-4:] == ".css" :
            global cssFileCount
            cssFileCount+=1
            return False
        elif parsedURL.path[len(parsedURL.path)-3:] == ".js":
            global jssFileCount
            jssFileCount+=1
            return False
        elif parsedURL.path[len(parsedURL.path)-3:] == ".png":
            global pngFileCount
            pngFileCount+=1
            return False
        elif parsedURL.path[len(parsedURL.path)-3:] == ".svg":
            global svgFileCount
            svgFileCount+=1
            return False
        else:
            return True
    else:
        #print("Invalid url: "+urlString+" path"+parsedURL.path)
        return False

# Checks if the host has a robots.txt file; if present, retrieves and stores disallowed directory paths using the parent URL in a set
def check_And_Process_Robot_txt_File(urlString):
    parsedURL=urlparse(urlString)
    parentUrl=parsedURL.scheme+"://"+parsedURL.netloc
    robotUrl= parentUrl+"/robots.txt"
    try:
        with urlopen(robotUrl,timeout=5) as robotContent:
            robots_txt = robotContent.read().decode('utf-8')
            #print("Robot.txt available in parentUrl:"+parentUrl+ " robot url: "+robotUrl,end=" ")
            for line in robots_txt.splitlines():
                # Check if the line starts with 'Disallow'
                if line.startswith('Disallow:'):
                    # Extract the value after 'Disallow:'
                    disallow_path = line.split(':', 1)[1].strip()
                    #disallow_rules.append(disallow_path)
                    global robot_txt_disallowed_urls
                    if "*"==disallow_path[0]:
                        disallow_path=disallow_path[1:] 
                    if len(disallow_path)>1:
                        robot_txt_disallowed_urls.add( parentUrl+disallow_path )
    except:
        pass
    


# Checks whether the site or directory is disallowed based on the stored robots.txt rules
def check_site_authorization_using_robot_file(url):
    global robot_txt_disallowed_urls
    for i in robot_txt_disallowed_urls:
        if i in url:
            print("Disallowed based on robot file: "+ url)
            return False
    return True


# For safety and efficiency in parsing large websites, a time limit is set for processing URLs on a webpage.
# This will increase the crawl count. Optimization can be done using multiple threads:
# 1. One for parsing/crawling and adding to the queue
# 2. Another for downloading the web pages
def getSubLinks(parentUrl,webContent,durationLimitForCrawling=120):
    currentTime=time.time()
    sublinksCount=0
    for sublinks in webContent.find_all(href=True):
        currentSublink=get_Absoulte_path(parentUrl.url,sublinks['href'])
        currentSublink=sublinks['href']
        global urlQueue
        domainName=get_Parsed_Domain(currentSublink)
        if parseAndvalidateURL(currentSublink) and not check_if_the_url_already_in_queue(currentSublink):
            heapq.heappush(urlQueue,([parentUrl.urlDepth+1,check_if_the_domain_already_in_queue_and_get_priority(domainName)], customQueue(currentSublink,parentUrl.urlDepth+1)))
            sublinksCount+=1
            seen_urls.add(sublinks['href'])
            seen_domains.add( domainName ) # Gets the parsed domain, so that it can used to check whether the domain is already in queue or seen
        if time.time()> (currentTime+durationLimitForCrawling):
            print("Exiting becasue time limit, total unverfifed links: "+len(webContent.find_all(href=True)))
            break
    return sublinksCount


# It counts the number of particular exceptions from exception list 
def get_Particular_Exception_Count(exceptlist,searchExceptionRegex):
    count=0
    for i in exceptlist:
        if searchExceptionRegex in i:
            count+=1
    return count


def start_the_crawler(seedlist,logFileName,durationOfCrawl):    
    global exceptionCountFor403,exceptionCountFor404,totalSizeOfCrawledData
    # Will append the 20 seeds by setting as Depth 1 and priorrity 1 as they are unique seeds
    for url in seedlist:
        with open(logFileName+"-seed-list.txt","a") as f:
            f.write(url+" ")
        url=url.replace("\n","")
        heapq.heappush(urlQueue,([1,1], customQueue(url,1)))
    global startTime
    startTime=time.time()
    while len(urlQueue)!=0:
        currentUrl=heapq.heappop(urlQueue)[1]
        tempstatus=0
        try:
            # Processes the robots.txt file to retrieve restricted paths for the host
            check_And_Process_Robot_txt_File(currentUrl.url)
            # Checks whether the URL is allowed to be crawled based on the stored restriction paths from the robots.txt file
            if not check_site_authorization_using_robot_file(currentUrl.url):
                continue
            with urlopen(currentUrl.url,timeout=5) as currentPageBody:
                try:
                    # This condition checks if the status is 200 and if the response is an HTML file; otherwise, it moves to the next iteration
                    if currentPageBody.getcode()!=200:
                        if currentPageBody.getcode()==403:
                            exceptionCountFor403+=1
                        elif currentPageBody.getcode()==404:
                            exceptionCountFor404+=1
                    elif currentPageBody.info().get_content_type() != 'text/html':
                        continue
                    webContent=BeautifulSoup(currentPageBody ,"html.parser")
                    #print(" Sub Links: "+str(getSubLinks(currentUrl,webContent)))
                    getSubLinks(currentUrl,webContent)
                    logString=str(currentUrl.url)+ " "+str(datetime.now())+" "+str(len(str(webContent)))+" "+str(currentUrl.urlDepth)+ " "+str(currentPageBody.getcode())
                    global totalSizeOfCrawledData 
                    totalSizeOfCrawledData+=len(str(webContent))
                    seen_urls.add(currentUrl.url)  # Store the url in seen list so that it will used to avoid duplicate urls in priority queue 
                    seen_domains.add(get_Parsed_Domain(currentUrl.url) ) # Gets the parsed domain, so that it can used to check whether the domain is already in queue or seen
                    # Stores the crawled link with the necessary data in the specified log file
                    with open(logFileName, 'a') as f:
                        f.write(logString+'\n')
                    global totalcrawls
                    totalcrawls+=1
                except Exception as innerError:
                    #print("Inner Exception:"+ str(innerError))
                    #traceback.print_exc()
                    global innerExceptionList
                    innerExceptionList.append(str(innerError)+" : "+str(currentUrl.url))
        except Exception as outerError:
            global exceptionlist
            exceptionlist.append(str(outerError)+" : "+str(currentUrl.url))
        if time.time()> (startTime+durationOfCrawl):
            print(" ***** Total crawls ="+str(totalcrawls)+ " **** ")
            break
    global cssFileCount,jssFileCount,svgFileCount,pngFileCount
    basic_analysis_log_string=" ***** Total crwals in "+str(time.time()-startTime)+" seconds = "+str(totalcrawls)+ " **** \n" +" Total Number of CSS files found = "+str(cssFileCount)+"\n Total Number of Js Files found = "+str(jssFileCount)+"\n Total Number of Png files found = "+str(pngFileCount)+"\n Total Number of Svg files found = "+str(svgFileCount) 
    with open(logFileName, 'a') as f:
        f.write(basic_analysis_log_string+'\n'+" Total number of 404 exceptions: "+str(exceptionCountFor404)+"\n Total number of 403 exceptions: "+str(exceptionCountFor403)+" \nTotal size of the crawled webpages: "+str(totalSizeOfCrawledData))




seedFile=open("/Users/rockramsri/Downloads/nz_domain_seeds_list.txt","r")
lines=seedFile.readlines()
random.shuffle(lines) # To get randomized seed list for each logs
start_the_crawler(lines[:20],"first_log_night2.txt",1800)


