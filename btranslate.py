# -*- coding=utf-8 -*-
from bs4 import BeautifulSoup
import urllib
import re
import json as jsonp
#from flask_pagination import Pagination 
import sys  
reload(sys)  
sys.setdefaultencoding('utf8') 

# system consts
translation_client_id = "DjlgYNflhGT8FQFEiWaG1EZd"

def translate(source, l_to="en", l_from="zh"):
    #if the source text is a list, put it into string first.
    if type(source) is list:
        is_list = True
        to_be_translated = []
        for item in source:
            if re.match(r'\s*$', item):
                item='-----'
            to_be_translated.append(item.replace("\n", "<brr/>"))
        string_to_be_translated = "\n".join(to_be_translated)
    else:
        is_list = False
        string_to_be_translated = source.replace("\n", "<brr/>")
    
    try:
        list_result = []
        string_result = ''
        while len(string_to_be_translated) > 0:
            print '=====batch====='+string_to_be_translated
            translate_this_time = string_to_be_translated[:100]
            print 'translate this time:', translate_this_time
            # if the last character of this batch is a '\n', consume one more character
            while translate_this_time[-1] == "\n":
                translate_this_time = string_to_be_translated[:len(translate_this_time)+1]
            url = "http://openapi.baidu.com/public/2.0/bmt/translate?client_id=%s&q=%s&from=%s&to=%s" % (translation_client_id,urllib.quote_plus(str(translate_this_time)), l_from, l_to)
            print url
            result = jsonp.loads(urllib.urlopen(url).read())
            print result
            #if the query is list, put the result string back to a list
            if not is_list:
                string_result=string_result+result["trans_result"][0]['dst']
            else: # for the list case
                i=0
                # if it's not the first batch, connect the first result to the last one in the list
                if len(list_result)>0:
                    str_result = result["trans_result"][i]['dst']
                    list_result[-1]=list_result[-1]+str_result
                    list_result[-1]=list_result[-1].replace("<brr/>","\n")
                    i=i+1
                while i<len(result["trans_result"]):
                    str_result = result["trans_result"][i]['dst']
                    if re.match(r'[-\s]+$', str_result):
                        str_result = ''
                    list_result.append(str_result.replace("<brr/>","\n"))
                    i=i+1
            # continue to the next batch
            string_to_be_translated = string_to_be_translated[len(translate_this_time):]
        if not is_list:
            return string_result.replace("<brr/>","\n")
        else:
            return list_result
    except Exception:
        return source