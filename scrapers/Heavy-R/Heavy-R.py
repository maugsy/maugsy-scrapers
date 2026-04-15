import cloudscraper
import json
import sys
import re
import base64
from lxml import html
from datetime import datetime, timedelta

def read_input():
    return json.loads(sys.stdin.read())

def scrape_url(url):
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        }
    )

    response = scraper.get(url)

    if response.status_code != 200:
        return {}

    tree = html.fromstring(response.content)
    result = {}

    try:
        title = tree.xpath('//h1[@class="video-title"]/text()')
        if title:
            result['Title'] = title[0].strip()
    except Exception:
        pass

    try:
        desc = tree.xpath('//h1[@class="video-title"]/following-sibling::p[1]//text()')
        if desc:
            result['Details'] = ' '.join(t.strip() for t in desc if t.strip())
    except Exception:
        pass

    try:
        date_raw = tree.xpath('//span[@class="block"]/text()')
        if date_raw:
            date_str = date_raw[0].strip()
            if re.search(r'today', date_str, re.IGNORECASE):
                result['Date'] = datetime.now().strftime('%Y-%m-%d')
            elif re.search(r'yesterday', date_str, re.IGNORECASE):
                result['Date'] = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            else:
                days_match = re.search(r'(\d+)\s+days?\s+ago', date_str, re.IGNORECASE)
                if days_match:
                    days = int(days_match.group(1))
                    result['Date'] = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    except Exception:
        pass

    try:
        tags = tree.xpath('//div[@class="tags"]//a/text()')
        if tags:
            result['Tags'] = [{'Name': t.strip()} for t in tags if t.strip() and '+ show all tags' not in t.lower()]
    except Exception:
        pass

    try:
        uploader_name = tree.xpath('//a[contains(@class,"black") and contains(@class,"underline") and starts-with(@href,"/user/")]/text()')
        uploader_url = tree.xpath('//a[contains(@class,"black") and contains(@class,"underline") and starts-with(@href,"/user/")]/@href')
        if uploader_name:
            result['Studio'] = {'Name': uploader_name[0].strip()}
            if uploader_url:
                result['Studio']['URL'] = 'https://www.heavy-r.com' + uploader_url[0].strip()
    except Exception:
        pass

    try:
        image_url = tree.xpath('//meta[@property="og:image"]/@content')
        if image_url:
            img_response = scraper.get(image_url[0].strip())
            if img_response.status_code == 200:
                img_b64 = base64.b64encode(img_response.content).decode('utf-8')
                mime_type = img_response.headers.get('Content-Type', 'image/jpeg')
                result['Image'] = f"data:{mime_type};base64,{img_b64}"
    except Exception:
        pass

    result['URLs'] = [url]
    return result

try:
    inp = read_input()
    if sys.argv[1] == "scrapeURL":
        ret = scrape_url(inp['url'])
        print(json.dumps(ret))
except Exception:
    print(json.dumps({}))
