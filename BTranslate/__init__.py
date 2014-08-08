import urllib
import json as jsonp

def translate(source, l_to="en", l_from="zh"):    
    translation_client_id = "DjlgYNflhGT8FQFEiWaG1EZd" # replace this to your own id for sustainable service!
    url = "http://openapi.baidu.com/public/2.0/bmt/translate?client_id=%s&q=%s&from=%s&to=%s" % (translation_client_id,urllib.quote_plus(str(source)), l_from, l_to)
    try:
        result = jsonp.loads(urllib.urlopen(url).read())
        dst = result["trans_result"][0]["dst"]
        return dst
    except Exception:
        return source