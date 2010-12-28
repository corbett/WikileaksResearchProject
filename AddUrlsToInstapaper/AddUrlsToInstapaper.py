#!/usr/bin/env python
# encoding: utf-8
"""
AddUrlsToInstapaper.py

Simple script to add all urls referenced in root url to instapaper. Depends on BeautifulSoup. Install with
% easy_install beautifulsoup

Author: Christine Corbett Moran
License: BSD
"""

import sys
import getopt
from BeautifulSoup import * 
from sets import Set
import urllib
import urllib2 

help_message = '''
./AddUrlsToInstapaper.py -w -u username -p password page_url

Adds all urls referenced on page_url to instapaper. If -w option is given, wikipedia urls are retained, if not they are ignored. The username and password option refer to instapaper username and optional password.
'''


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def add_links_to_instapaper(url,username,password=None,
    wikilinks=False,verbose=False):    
    def valid_link(link):
    	return ('http' in link) and (wikilinks or not 'wikipedia.org' in link)
    INSTAPAPER_ADD='https://www.instapaper.com/api/add'
    instapaper_params={'username':username}
    if password: 
        instapaper_params['password']=password
    # spoofing user agent headers, some sites like Wikipedia require
    opener=urllib2.build_opener()
    opener.addheaders =[('User-agent', 'Mozilla/5.0')] 
    wikipedia_page=BeautifulSoup(opener.open(url).read()) 
    all_links=Set()
    for link in wikipedia_page.findAll('a'):
        try:
            link=link['href']
            if not link in all_links and valid_link(link):
			    instapaper_params['url']=link
			    result=urllib.urlopen(INSTAPAPER_ADD+'?%s' % urllib.urlencode(instapaper_params))
			    if verbose:
			        print 'status code %s for adding %s to instapaper' % (result.read(),link)		
            all_links.add(link)        		
        except:
            continue
            
def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hvwu:p:",
                ["help","verbose","wikilinks","username","password"])
        except getopt.error, msg:
            raise Usage(msg)
        # option processing
        password,verbose,wikilinks,username,password=[None]*5
        for option, value in opts:
            if option == "-v":
                verbose = True
            if option in ("-h", "--help"):
                raise Usage(help_message)
            if option in ("-w","wikilinks"):
                wikilinks=True
            if option in ("-u","username"):
                username=value
            if option in ("-p","password"):
                password=value
        if not len(args)==1 or not username:
            raise Usage(help_message)
        page_url=args[0]
        add_links_to_instapaper(page_url,username,
            password=password,wikilinks=wikilinks,verbose=verbose)
    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2


if __name__ == "__main__":
    sys.exit(main())
