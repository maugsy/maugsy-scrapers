import cloudscraper
import json
import sys
import re
import base64
from lxml import html

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
        title = tree.xpath('//h1[@class="title-right"]/text()')
        if title:
            result['Title'] = title[0].strip()
    except Exception:
        pass

    try:
        descs = tree.xpath('//div[@class="player-info-desc"]/div[@class="player-desc"]')
        for div in descs:
            child_spans = div.xpath('.//span[@class="channelLinks" or @class="tagLinks"]')
            if not child_spans:
                sprite_spans = div.xpath('.//span[contains(@class,"sprite-icon")]')
                if not sprite_spans:
                    text = div.text_content().strip()
                    if text:
                        result['Details'] = text
                        break
    except Exception:
        pass

    try:
        all_tags = []
        category_tags = tree.xpath('//span[@class="channelLinks"]/a/text()')
        for t in category_tags:
            t = t.strip()
            if t:
                all_tags.append({'Name': t})
        tag_tags = tree.xpath('//span[@class="tagLinks"]/a/text()')
        for t in tag_tags:
            t = t.strip()
            if t and {'Name': t} not in all_tags:
                all_tags.append({'Name': t})
        if all_tags:
            result['Tags'] = all_tags
    except Exception:
        pass

    try:
        json_ld = tree.xpath('//script[@type="application/ld+json"]/text()')
        for block in json_ld:
            try:
                data = json.loads(block)
                if 'thumbnailUrl' in data:
                    img_url = data['thumbnailUrl']
                    img_response = scraper.get(img_url)
                    if img_response.status_code == 200:
                        img_b64 = base64.b64encode(img_response.content).decode('utf-8')
                        mime_type = img_response.headers.get('Content-Type', 'image/jpeg')
                        result['Image'] = f"data:{mime_type};base64,{img_b64}"
                    break
            except Exception:
                continue
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
