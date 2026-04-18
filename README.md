# maugsy-scrapers

A collection of [Stash](https://github.com/stashapp/stash) scrapers made by maugsy

## Source index URL
<https://maugsy.github.io/maugsy-scrapers/main/index.yml>

## Scrapers
- **DarknessPorn** - scrapes **Title**, **Date**, **Tags**, and **Thumbnail image**
- **Heavy-R** - scrapes **Title**, **Description**, **Date**, **Tags**, **Studio** (uploader), and **Thumbnail image**
- **LuxureTV** - scrapes **Title**, **Description**, **Tags**, and **Thumbnail image**
- **Punishworld** (*New in v1.2*) - scrapes **Title**, **Performers**, **Date**, **Tags**, and **Thumbnail image**
- **SickJunk** (*Added in v1.1*) - scrapes **Title**, **Description**, **Date**, **Tags**, and **Thumbnail image**

## Installation
In Stash, go to **Settings → Metadata Providers → Add Source** and paste the source index URL above

## Dependencies
Make sure you have the following Python packages installed:
- cloudscraper
- lxml
- requests

```pip install cloudscraper lxml requests```
