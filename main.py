# -*- coding=utf-8 -*-
from bs4 import BeautifulSoup
import urllib
import re
import json as jsonp
import time
from BTranslate import translate
from flask import Flask, render_template, request, jsonify, session
from flask.ext.socketio import SocketIO, emit
#from flask_pagination import Pagination 
import sys  
reload(sys)  
sys.setdefaultencoding('utf8') 

# system consts
translation_client_id = "DjlgYNflhGT8FQFEiWaG1EZd"
records_per_page = 10
job_timestamp = "" # current job timestamp - if changed stop the job

app = Flask(__name__)
app.debug=True
app.config['SECRET_KEY'] = '53e3e99ff076f53e3e9aaaba4d!'
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route('/hot_search_terms')
def hot_search_terms():
    url = "http://news.baidu.com/n?m=rddata&v=hot_word"
    jsons = urllib.urlopen(url).read().decode('utf-8', 'ignore')
    terms = jsonp.loads(jsons)['data']
    for term in terms:
        term['title'] = translate(term['title'])
    return jsonify(result=terms)

@socketio.on("search", namespace="/wdtcs")
def wdtcs_search(msg):
    session['job_timestamp'] = time.time()
    if 'keyword' in msg:
        key = msg['keyword']
    else:
        print "need to provide keyword"
    # default page = 1
    if 'page' in msg:
        page = int(msg['page'])
    else:
        page = 1
    # default type = news
    if 'type' in msg:
        result_type = msg['type']
    else:
        result_type = "news"
    #translated 
    if 'translate' in msg:
        translated = True
    else:
        translated = False
    if 'translate_input' in msg:
        translate_input = True
    else:
        translate_input = False
    #the real thing!
    if result_type == 'weibo':
        scrape_weibo(keywords=key, page=page, translated=translated, translate_input=translate_input)
    else:
        scrape_baidu(keywords=key, type=result_type, page=page, translated=translated, translate_input=translate_input)



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
    ts = session['job_timestamp']  # keep a snapshot of the timestamp
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
       emit('show next page', {})
    else:
       emit('hide next page', {})
    for record in news:
        print "-------ts--------", ts, session['job_timestamp']
        if ts != session['job_timestamp']:
            return
        a_tag = record.find('a')
        title = get_soup_text(a_tag)
        link = a_tag['href']
        content = get_content_soup_text(record.find('h3').next_sibling)
        if translated:
            emit('result', {'title': translate(title), 'link': link, 'content': translate(content)})
        else:
            emit('result', {'title': title, 'link': link, 'content': content})
    emit('end loading', {})

def scrape_weibo(keywords, page=1, translated=False, translate_input=False):
    pn = str((page-1)*10)
    ts = job_timestamp
    if translate_input:
        keywords = translate(keywords, l_from="en", l_to="zh").encode('utf-8')
    url = "http://www.baidu.com/s?tn=baiduwb&rtt=2&cl=2&ie=utf-8&wd=%s&pn=%s" % (keywords, pn)
    f = urllib.urlopen(url)
    soup = BeautifulSoup(f.read().decode('utf-8', 'ignore'))
    news = soup.select('#weibo li')
    result = []
    next_page_link = soup.find('a', text="下一页>")
    if next_page_link:
        emit('show next page', {})
    else:
        emit('hide next page', {})
    for record in news:
        if ts != job_timestamp:
            return
        a_tag = record.select('a.weibo_all')
        link = a_tag[0]['href']
        content = get_soup_text(record.find('p'))
        if translated:
            emit('result', {'link': link, 'content': translate(content)})
        else:
            emit('result', {'link': link, 'content': content})
	emit('end loading', {})


if __name__ == "__main__":
    socketio.run(app)