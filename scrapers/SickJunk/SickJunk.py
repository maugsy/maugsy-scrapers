import cloudscraper
import json
import sys
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
        title = tree.xpath('//h1[contains(@class,"entry-title")]/text()')
        if title:
            result['Title'] = title[0].strip()
    except Exception:
        pass

    try:
        date_attr = tree.xpath('//time[contains(@class,"entry-date")]/@datetime')
        if date_attr:
            result['Date'] = date_attr[0][:10]
    except Exception:
        pass

    try:
        all_tags = []
        category_tags = tree.xpath('//div[contains(@class,"awaken-category-list")]//a/text()')
        for t in category_tags:
            t = t.strip()
            if t:
                all_tags.append({'Name': t})
        tag_tags = tree.xpath('//div[contains(@class,"awaken-tag-list")]//a/text()')
        for t in tag_tags:
            t = t.strip()
            if t and {'Name': t} not in all_tags:
                all_tags.append({'Name': t})
        if all_tags:
            result['Tags'] = all_tags
    except Exception:
        pass

    try:
        content_divs = tree.xpath('//div[contains(@class,"entry-content")]')
        if content_divs:
            paragraphs = []
            for child in content_divs[0]:
                tag = child.tag if isinstance(child.tag, str) else ''
                classes = child.get('class', '')
                if tag == 'hr' and 'wp-block-separator' in classes:
                    break
                if tag == 'p':
                    text = child.text_content().strip()
                    if text:
                        paragraphs.append(text)
            if paragraphs:
                result['Details'] = '\n\n'.join(paragraphs)
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
