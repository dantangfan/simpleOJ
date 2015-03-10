#coding=utf-8
from BeautifulSoup import BeautifulSoup
import re
regex_cache = {}

def search(text, regex):
    regexcmp = regex_cache.get(regex)
    if not regexcmp:
        regexcmp = re.compile(regex)
        regex_cache[regex] = regexcmp
    return regexcmp.search(text)

# XSS白名单
VALID_TAGS = {'h1':{}, 'h2':{}, 'h3':{}, 'h4':{}, 'strong':{}, 'em':{}, 
              'p':{}, 'ul':{}, 'li':{}, 'br':{}, 'a':{'href':'^http://', 'title':'.*'}, 
              'img':{'src':'^http://', 'alt':'.*'}, 'pre':{}}

def parsehtml(html):
    soup = BeautifulSoup(html)
    for tag in soup.findAll(True):
        if tag.name not in VALID_TAGS:
            tag.hidden = True
        else:
            attr_rules = VALID_TAGS[tag.name]
            for attr_name, attr_value in tag.attrs:
                #检查属性类型
                if attr_name not in attr_rules:
                    del tag[attr_name]
                    continue
                    
                #检查属性值格式
                if not search(attr_value, attr_rules[attr_name]):
                    del tag[attr_name]
                
                        
    return soup.renderContents()