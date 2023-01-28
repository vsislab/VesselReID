from urllib.request import urlopen
import urllib.request as request
import requests
import random 
import re
import time
from urllib.parse import urlencode
import http.cookiejar as cookielib 
from retrying import retry 
import gc
import gzip 
import urllib.error 
import argparse
import os
import json


parser = argparse.ArgumentParser(description='Downloading and splitting VesselReID datasets')

parser.add_argument('--pth',
                        help='Address of the dataset annotation file',
                        type=str,
                        default='./VesselReID.json')
parser.add_argument('--save_pth',
                        help='Download save dataset address',
                        type=str,
                        default='./VesselReID')


def select_proxy(proxy_type='socks-client'):
    proxies = {}
    if proxy_type == 'http':
        # Proxy settings：http(s) proxy
        proxies = {
            'https': 'https://127.0.0.1:2173',
            'http': 'http://127.0.0.1:2173'
        }
    elif proxy_type == 'socks-remote':
        # Proxy settings：socks5 proxy (remote servers)
        proxies = {
            'socks5': 'socks5://user:pass@host:port',
            'socks5': 'socks5://user:pass@host:port'
        }
    elif proxy_type == 'socks-client':
        # Proxy settings：socks5 proxy (client locally)
        proxies = {
            'http': 'socks5://127.0.0.1:2080',
            'https': 'socks5://127.0.0.1:2080'
        }
    elif proxy_type == 'no':
        # Proxy settings：No proxies
        proxies = {}
    else:
        pass
    return proxies


@retry(stop_max_attempt_number=5, wait_random_min=10, wait_random_max=20)    # Set the number of request failures

def get_data(url):
    proxies = select_proxy('socks-remote')
    agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
    headers = {
        'user-agent': agent,
    }
    print('Get data from the web page ...')
    cookie = cookielib.CookieJar()    
    request.build_opener()
    opener = request.build_opener(request.ProxyHandler(proxies), request.HTTPCookieProcessor(cookie))    # Setting up proxies and cookie processors
    request.install_opener(opener)   
    req = request.Request(url, headers=headers)    # Setting requests
    try:
        response = request.urlopen(req)    # Access to the url
        print("Connection Succeeded!")
        if response.info().get('Content-Encoding') == 'gzip':
            data = gzip.decompress(response.read()).decode("utf-8")    # Unzip if in compressed format
        else:
            data = response.read()
        del cookie
        del opener
        response.close()
        del response
        gc.collect()
        return data
    except urllib.error.URLError as e:
        print('GoogleScholar.get_data()：' + str(e.reason))
    return
def mkdir(path):
    path=path.strip()
    path=path.rstrip("\\")
    isExists=os.path.exists(path)
    if not isExists:
        os.makedirs(path) 
        print (path+' Successful Creation!')
        return True
    else:
        print (path+' Catalogues already exist!')
        return False
        
def open_json(json_fth):
    if '.json' not in json_fth:
        print('Wrong file address, please enter the JSON file address !')
    with open(json_fth,'r') as f:
        json_f = json.load(f)
    return json_f

def download_img(url, img_name, split_info, save_pth='./'):
    img = get_data(url)
    datasets_type = ['normal', 'extra']
    for dt in datasets_type:
        if split_info[dt] != None:
            pths = f'{save_pth}/{dt}_split/{split_info[dt]}'
            img_pth = f'{pths}/{img_name}'
            mkdir(pths)
            with open(img_pth, 'wb') as f:
                f.write(img)
        
if __name__=='__main__':
    args = parser.parse_args()
    
    data = open_json(args.pth)        # Loading annotation files
    save_root = args.save_pth
    
    for img in data['images']:
        img_name = img['name']
        download_url = img['url']
        
        download_img(download_url, img_name, img['split'], save_pth=save_root)
        
        