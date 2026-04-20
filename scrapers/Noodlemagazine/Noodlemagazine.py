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
        json_ld = tree.xpath('//script[@type="application/ld+json"]/text()')
        for block in json_ld:
            try:
                data = json.loads(block)

                if data.get('@type') != 'VideoObject':
                    continue

                try:
                    name = data.get('name')
                    if name:
                        result['Title'] = name.strip()
                except Exception:
                    pass

                try:
                    upload_date = data.get('uploadDate')
                    if upload_date:
                        result['Date'] = upload_date[:10]
                except Exception:
                    pass

                try:
                    keywords = data.get('keywords', '')
                    if keywords:
                        all_tags = []
                        for t in keywords.split(','):
                            t = t.strip()
                            if t:
                                all_tags.append({'Name': t})
                        if all_tags:
                            result['Tags'] = all_tags
                except Exception:
                    pass

                try:
                    thumbnail = data.get('thumbnailUrl')
                    if thumbnail:
                        img_url = thumbnail[0] if isinstance(thumbnail, list) else thumbnail
                        img_response = scraper.get(img_url)
                        if img_response.status_code == 200:
                            img_b64 = base64.b64encode(img_response.content).decode('utf-8')
                            mime_type = img_response.headers.get('Content-Type', 'image/jpeg')
                            result['Image'] = f"data:{mime_type};base64,{img_b64}"
                except Exception:
                    pass

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
