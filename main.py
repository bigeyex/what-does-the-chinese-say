# -*- coding=utf-8 -*-
from bs4 import BeautifulSoup
import urllib
import re
import sqlite3
import json as jsonp
from flask import Flask, render_template, request, jsonify
#from flask_pagination import Pagination 
import sys  
reload(sys)  
sys.setdefaultencoding('utf8') 

# system consts
translation_client_id = "DjlgYNflhGT8FQFEiWaG1EZd"
records_per_page = 10

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/json")
def json():
    if 's' in request.args:
        key = request.args['s']
    else:
        return jsonify(error="You must provide search terms")
    # default page = 1
    if 'page' in request.args:
        page = int(request.args['page'])
    else:
        page = 1
    # default type = news
    if 'type' in request.args:
        result_type = request.args['type']
    else:
        result_type = "news"
    #translated 
    if 'translate' in request.args:
        translated = True
    else:
        translated = False
    if 'translate_input' in request.args:
        translate_input = True
    else:
        translate_input = False
    #the real thing!
    if result_type == 'weibo':
        print "weibo: key=%s, page=%s, translated=%s, input=%s" % (key, page, translated, translate_input)
        result = scrape_weibo(keywords=key, page=page, translated=translated, translate_input=translate_input)
    else:
        print "news: key=%s, page=%s, translated=%s, input=%s" % (key, page, translated, translate_input)
        result = scrape_baidu(keywords=key, type=result_type, page=page, translated=translated, translate_input=translate_input)
    return jsonify(result=result['result'], has_next_page=result['has_next_page'])

# code for scraper

def get_soup_text(soup):
	return re.sub('<[^<]+?>', '', str(soup))
	
def get_content_soup_text(soup):
	result = str(soup)
	result = re.sub('<div[^>]*>.*?<\/div>', '', result)
	result = re.sub('<br\/>.*', '', result)
	result = re.sub('<[^<]+?>', '', result)
	return result

def scrape_baidu(keywords, page=1, type='news', translated=False, translate_input=False):
	pn = str((page-1)*10)
	if translate_input:
		keywords = translate(keywords, l_from="en", l_to="zh").encode('utf-8')
	if type=='blog':
		url = "http://www.baidu.com/s?tn=baidurt&rtt=1&wd=%s&pbl=1&pbs=0&bsst=1&pn=%s&ie=utf-8" % (keywords, pn)
	elif type=='forum':
		url = "http://www.baidu.com/s?tn=baidurt&rtt=1&wd=%s&pbs=1&bsst=1&pn=%s&ie=utf-8" % (keywords, pn)
	else:
		url = "http://www.baidu.com/s?tn=baidurt&rtt=1&wd=%s&pnw=1&pbl=0&pbs=0&bsst=1&ie=utf-8&pn=%s" % (keywords, pn)
	f = urllib.urlopen(url)
	soup = BeautifulSoup(f.read().decode('utf-8', 'ignore'))
	news = soup.select('td.f')
	result = []
	next_page_link = soup.find('a', text="下一页>")
	if next_page_link:
		has_next_page = True
	else:
		has_next_page = False
	for record in news:
		a_tag = record.find('a')
		title = get_soup_text(a_tag)
		link = a_tag['href']
		content = get_content_soup_text(record.find('h3').next_sibling)
		if translated:
			result.append({'title': translate(title), 'link': link, 'content': translate(content)})
		else:
			result.append({'title': title, 'link': link, 'content': content})
	return {'result':result, 'has_next_page': has_next_page}

def scrape_weibo(keywords, page=1, translated=False, translate_input=False):
	pn = str((page-1)*10)
	if translate_input:
		keywords = translate(keywords, l_from="en", l_to="zh").encode('utf-8')
	url = "http://www.baidu.com/s?tn=baiduwb&rtt=2&cl=2&ie=utf-8&wd=%s&pn=%s" % (keywords, pn)
	f = urllib.urlopen(url)
	soup = BeautifulSoup(f.read().decode('utf-8', 'ignore'))
	news = soup.select('#weibo li')
	result = []
	next_page_link = soup.find('a', text="下一页>")
	if next_page_link:
		has_next_page = True
	else:
		has_next_page = False
	for record in news:
		a_tag = record.select('a.weibo_all')
		link = a_tag[0]['href']
		content = get_soup_text(record.find('p'))
		if translated:
			result.append({'link': link, 'content': translate(content)})
		else:
			result.append({'link': link, 'content': content})
	return {'result':result, 'has_next_page': has_next_page}
	
def translate_old(source, l_from='zh', l_to='en'):
    url = "http://openapi.baidu.com/public/2.0/bmt/translate?client_id=DjlgYNflhGT8FQFEiWaG1EZd&q=%s&from=%s&to=%s" % (urllib.quote_plus(source), l_from, l_to)
    result = jsonp.loads(urllib.urlopen(url).read())
    return result["trans_result"][0]["dst"]
				
# print scrape_weibo('Obama', translated=True, translate_input=True)

def translate(source, l_to="en", l_from="zh"):
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()
    sql = 'create table if not exists cache_table (id integer primary key, src text, dst text, l_to text)'
    cursor.execute(sql)
    conn.commit()
    cursor.execute("select * from cache_table where src=? and l_to=?", (unicode(source), l_to))
    line = cursor.fetchone()
    if line == None:
        url = "http://openapi.baidu.com/public/2.0/bmt/translate?client_id=%s&q=%s&from=%s&to=%s" % (translation_client_id,urllib.quote_plus(source), l_from, l_to)
        try:
            result = jsonp.loads(urllib.urlopen(url).read())
            print result
            dst = result["trans_result"][0]["dst"]
            cursor.execute("insert into cache_table (src, dst, l_to) values (?,?,?)", (unicode(source), unicode(dst), l_to))
            conn.commit()
            return dst
        except Exception:
            return source
    else:
        return line[2]

if __name__ == "__main__":
    app.run(debug=True)