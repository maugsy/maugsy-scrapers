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

    try:
        video_data_raw = tree.xpath('//div[@id="video-data"]/text()')
        if video_data_raw:
            video_data = json.loads(video_data_raw[0].strip())
            tags_str = video_data.get('tags', '')
            if tags_str:
                result['Tags'] = [{'Name': t.strip()} for t in tags_str.split(',') if t.strip()]
    except Exception:
        pass

    try:
        performer_elements = tree.xpath('//a[contains(@class,"badge-kiss")]')
        performers = []
        for el in performer_elements:
            name = el.text_content().strip()
            href = el.get('href', '').strip()
            if name:
                performer = {'Name': name}
                if href:
                    performer['URL'] = href
                performers.append(performer)
        if performers:
            result['Performers'] = performers
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
