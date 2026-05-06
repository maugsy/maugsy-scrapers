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

                title = data.get('name')
                if title:
                    result['Title'] = title.strip()

                description = data.get('description', '').strip()
                if description and description.lower() != 'no description provided':
                    result['Details'] = description

                upload_date = data.get('uploadDate')
                if upload_date:
                    result['Date'] = upload_date[:10]

                thumbnail = data.get('thumbnailUrl')
                if thumbnail:
                    img_url = thumbnail if isinstance(thumbnail, str) else thumbnail[0]
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
