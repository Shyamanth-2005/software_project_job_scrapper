import re
import time
import random
import pandas as pd
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def create_driver(headless: bool = True) -> webdriver.Chrome:
    """Create and return a Chrome WebDriver using webdriver-manager.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    if headless:
        try:
            options.add_argument('--headless=new')
        except Exception:
            options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def _text_or_none(el):
    return el.get_text(strip=True) if el else None


def scrape_naukri(pages: int = 10, headless: bool = True, debug: bool = False) -> list:
    """Scrape job data from Naukri data-science search results.

    Returns a list of dicts with fields extracted from each job card.
    """
    base_url = fr"https://www.naukri.com/jobs-in-india?clusters=functionalAreaGid&functionAreaIdGid=2&functionAreaIdGid=3&functionAreaIdGid=4&functionAreaIdGid=5&functionAreaIdGid=6&functionAreaIdGid=7&functionAreaIdGid=8&functionAreaIdGid=9&functionAreaIdGid=10&functionAreaIdGid=11&functionAreaIdGid=12&functionAreaIdGid=13&functionAreaIdGid=14&functionAreaIdGid=15&functionAreaIdGid=16&functionAreaIdGid=19&functionAreaIdGid=30&functionAreaIdGid=31&functionAreaIdGid=35"
    driver = create_driver(headless=headless)
    wait = WebDriverWait(driver, 10)
    records = []

    try:
        for page in range(1, pages + 1):
            url = base_url[:36]+ ("-" + str(page) if page != 1 else "") + base_url[36:]
            print(url)
            driver.get(url)

            time.sleep(2)

            if debug:
                print('\n--- Visiting', url)
                print('Window handles:', driver.window_handles)

            try:
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(1)
                driver.execute_script('window.scrollTo(0, 0);')
            except Exception:
                pass

            page_source = None
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                if debug:
                    print('Switched to handle:', handle, 'title:', driver.title[:80])
                try:
                    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".jobTuple, .cust-job-tuple, .sjw__tuple")))
                    page_source = driver.page_source
                    if debug:
                        print('Found job cards via wait in this handle')
                    break
                except Exception:
                    src = driver.page_source or ''
                    cnt_jobtuple = src.count('jobTuple') + src.count('cust-job-tuple') + src.count('sjw__tuple')
                    if debug:
                        print('jobTuple-like string occurrences in this handle:', cnt_jobtuple)
                    if cnt_jobtuple > 0:
                        page_source = src
                        if debug:
                            print('Found job cards via string check in this handle')
                        break
                    continue

            if page_source is None:
                page_source = driver.page_source

            time.sleep(random.uniform(0.5, 2.0))

            soup = BeautifulSoup(page_source, 'lxml')

            selectors = {'jobTuple', 'cust-job-tuple', 'sjw__tuple'}

            def is_job_card(tag):
                if tag.name != 'div':
                    return False
                classes = tag.get('class') or []
                for c in classes:
                    if c in selectors or any(s in c for s in selectors):
                        return True
                return False

            cards = soup.find_all(is_job_card)

            if not cards:
                title_anchors = soup.find_all('a', attrs={'class': lambda v: v and 'title' in v})
                cards = []
                for a in title_anchors:
                    parent = a
                    for _ in range(4):
                        parent = parent.parent
                        if parent is None:
                            break
                        if parent.name == 'div':
                            classes = parent.get('class') or []
                            cards.append(parent)
                            break

            if debug:
                print('soup length:', len(page_source) if page_source else 0)
                print('Found candidate cards:', len(cards))

            for card in cards:
                try:
                    title_anchor = card.find('a', attrs={'class': lambda v: v and 'title' in v})
                    if not title_anchor:
                        h2 = card.find('h2')
                        if h2:
                            title_anchor = h2.find('a')

                    job_title = _text_or_none(title_anchor)
                    job_url = title_anchor.get('href') if title_anchor and title_anchor.has_attr('href') else None

                    company_anchor = card.find('a', attrs={'class': lambda v: v and 'comp-name' in v})
                    company = _text_or_none(company_anchor)
                    company_url = company_anchor.get('href') if company_anchor and company_anchor.has_attr('href') else None

                    rating = None
                    reviews = None
                    rating_anchor = card.find('a', attrs={'class': lambda v: v and 'rating' in v})
                    if rating_anchor:
                        main2 = rating_anchor.find(class_=re.compile(r'main-2'))
                        if main2:
                            try:
                                rating = float(main2.get_text(strip=True))
                            except Exception:
                                rating = _text_or_none(main2)
                    review_anchor = card.find('a', attrs={'class': lambda v: v and 'review' in v})
                    if review_anchor:
                        rv_txt = review_anchor.get_text(strip=True)
                        m = re.search(r'(\d+[\d,]*)', rv_txt.replace('\u00a0', ' '))
                        if m:
                            try:
                                reviews = int(m.group(1).replace(',', ''))
                            except Exception:
                                reviews = m.group(1)

                    exp = None
                    exp_el = card.find('span', attrs={'title': re.compile(r'.*Yrs.*', re.I)}) or card.find(class_=re.compile(r'expwdth|exp-wrap|exp'))
                    if exp_el:
                        exp = _text_or_none(exp_el)

                    salary = None
                    sal_el = card.find(class_=re.compile(r'sal-wrap|sal|salary')) or card.find('span', attrs={'title': re.compile(r'.*Lacs.*|.*PA.*', re.I)})
                    if sal_el:
                        salary = _text_or_none(sal_el)

                    location = None
                    loc_el = card.find(class_=re.compile(r'locWdth|loc-wrap|loc')) or card.find('span', attrs={'title': re.compile(r'.*', re.I)})
                    if loc_el:
                        location = _text_or_none(loc_el)

                    desc_el = card.find('span', class_=re.compile(r'job-desc|jobDesc|ni-job-tuple-icon-srp-description'))
                    description = _text_or_none(desc_el)

                    tags = None
                    tags_ul = card.find('ul', class_=re.compile(r'tags-gt|tags'))
                    if tags_ul:
                        tags_list = [li.get_text(strip=True) for li in tags_ul.find_all('li')]
                        tags = ';'.join(tags_list)

                    posted = None
                    posted_el = card.find(class_=re.compile(r'job-post-day|post-day'))
                    if posted_el:
                        posted = _text_or_none(posted_el)

                    record = {
                        'job_title': job_title,
                        'job_url': job_url,
                        'company': company,
                        'company_url': company_url,
                        'rating': rating,
                        'reviews': reviews,
                        'experience': exp,
                        'salary': salary,
                        'location': location,
                        'description': description,
                        'tags': tags,
                        'posted': posted
                    }

                    if record['job_url'] or record['job_title']:
                        records.append(record)

                except Exception as e:
                    if debug:
                        print('Error parsing card:', e)
                    continue

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    unique = []
    seen = set()
    for r in records:
        key = r.get('job_url') or r.get('job_title')
        if not key:
            continue
        if key not in seen:
            seen.add(key)
            unique.append(r)

    return unique


if __name__ == '__main__':
    items = scrape_naukri(pages=25, headless=False, debug=True)
    print(f'Collected {len(items)} job records')
    if items:
        df = pd.DataFrame(items)
        df.to_csv('naukri_jobs.csv', index=False)
        print('Saved to naukri_jobs.csv')
    else:
        print('No items found; check debug output to diagnose.')