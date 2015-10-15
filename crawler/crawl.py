""" Contains functionality to crawl webpages for text.

    Usage example:

        >>> htmls = crawl.crawl_urls(urls)
        >>> htmls = crawl.crawl_urls(urls, max_depth=1) # no link recursion

 """
from bs4 import BeautifulSoup
import requests
import shelve
from urllib import unquote
from urlparse import urljoin, urlparse

from config import get_config
from crawler import text_extraction, text_utils
from crawler.io_fs import IoFs
from crawler.io_rethinkdb import IoRethinkdb

# Global variable to keep track of already visited urls
visited = []
# Global variable to store the crawler i/o instance
crawler_io = None


def get_crawler_io():
    """ Return the instance that handles crawler I/O functionality for
        caching and keeping track of redirect and error URLs.

        Is a `IoRethinkdb` instance if CRAWLER_USE_RETHINK is True else `IoFs`.

    """
    global crawler_io
    if crawler_io is None:
        if get_config('CRAWLER_USE_RETHINK'):
            crawler_io = IoRethinkdb(
                get_config('DB_HOST'), get_config('DB_PORT'))
        else:
            crawler_io = IoFs(get_config('CRAWLER_PATH'))
    return crawler_io


def get_top_domain(url):
    """ Extract the domain name from a url.

        :param url: URL of the webpage.

    """
    return '.'.join(urlparse(url).netloc.split('.')[-2:])


def add_scheme(url):
    """ Add `http` scheme to URL. """
    o = urlparse(url)
    if not o.scheme:
        return 'http://' + url
    return url


def filter_url(start_url, url):
    """ Filter out URLs that do not match certain criteria such as non-html,
        already visited, or external URLs.

        :param start_url: URL of the webpage that initiated the process.
                          Useful to check if a URL is external or not.
        :param url: URL of the webpage to be filtered.

    """
    if (urlparse(start_url).scheme != 'http' and
            urlparse(start_url).scheme != 'https'):
        return True
    if urlparse(url).scheme != 'http' and urlparse(url).scheme != 'https':
        return True
    if url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        return True
    if url.startswith('mailto:'):
        return True
    if url in visited:
        return True
    if get_top_domain(start_url) != get_top_domain(url):
        return True
    path = urlparse(url).path
    filename = path.split('/')[-1]
    if filename.find('.') == -1:
        return False
    if filename.lower().endswith(('.html', '.htm', '.shtm', '.shtml', '.php',
                                  '.jsp', '.aspx', '.asp')):
        return False
    if filename.lower().endswith(('.pdf')):
        return False
    if get_config('CRAWLER_VERBOSE'):
        print 'filtered out ', url
    return True


def clean_url(url):
    """ Clean URL in order to avoid redundancy, e.g. two URLs linking to the
        same page. Currently just gets rid of fragments and slash character
        at the end.

    """
    # Remove fragment
    if '#' in url:
        url = url[:url.index('#')]
    # Remove slash at the end
    if not urlparse(url).path:
        url += '/'
    try:
        url = unquote(url.encode('utf8')).decode('utf8')
    except Exception:
        url = unquote(url.encode('latin-1')).decode('latin-1')
    return url


def extract_content_url(s):
    """ Extract the url from the content element in the meta html tag. """
    for elem in s.split(';'):
        keyvalue = elem.split('=')
        if keyvalue[0] == 'url' and len(keyvalue) > 1:
            return keyvalue[1]
    return ''


def extract_links(url, html=None):
    """ Get all hyperlinks from a webpage.

        :param url: URL of the webpage.
        :param html: Contents of the already downloaded url.

    """
    if html is None:
        html = download(url)
    soup = BeautifulSoup(html)
    return set([urljoin(url, tag['href'].strip())
               for tag in soup.findAll('a', href=True)]
               + [urljoin(url, tag['src'].strip())
                  for tag in soup.findAll('frame', src=True)]
               + [urljoin(url, tag['val0'].strip())
                  for tag in soup.findAll('csaction', val0=True)]
               + [urljoin(url, extract_content_url(tag['content']).strip())
                  for tag in soup.findAll('meta', content=True)]
               )


def download(url):
    """ Return the contents of the URL in the argument. The `crawler_io`
        object will be used to cache the requests and keep track of redirect
        and error URLs.

        :param url: URL to download.

    """
    crawler_io = get_crawler_io()
    if crawler_io.is_error_url(url):
        return None
    text = crawler_io.load_str(url)
    if text:
        if get_config('CRAWLER_VERBOSE'):
            print 'cached', url
    else:
        if get_config('CRAWLER_VERBOSE'):
            print 'downloading', url
        try:
            response = requests.get(url)
        except Exception:
            crawler_io.add_error_url(url)
            return None
        if response.status_code >= 400:
            crawler_io.add_error_url(url)
            return None
        crawler_io.add_redirect(url, response.url)
        text = response.content
        crawler_io.save_str(url, text)
    return text


def extract_html_rec(start_url, max_depth=99, url=None, max_links=None):
    """ Recursively extract all HTMLs from a start URL.

        :param start_url: URL of the initial webpage.
        :param url: URL of the webpage. Used internaly for the recursive calls.
                    Always use None when calling this function from another
                    function.
        :param max_depth: Depth of crawling.

    """
    global visited
    if url is None:
        url = start_url
        visited = []
    if max_depth == 0:
        return []
    if max_links is not None and (len(visited) >= max_links):
        return []
    url = clean_url(url)
    visited.append(url)
    html = download(url)
    if html is None:
        return []
    text = [html]
    if not text_extraction.is_pdf(html):
        for link in extract_links(
                get_crawler_io().get_redirect(url),
                text_utils.str2unicode(html)):
            link = clean_url(link)
            if not filter_url(start_url, link):
                text = text + extract_html_rec(
                    start_url, max_depth-1, link, max_links)
    return text


def crawl_url(url, max_depth=1, max_links=None):
    """ Call `crawl_urls` with a single URL. """
    return crawl_urls([url], max_depth=max_depth, max_links=max_links)


def crawl_urls(urls, max_depth=1, max_links=None, cache_htmls=False,
               shelve_db='html_cache.db', append_htmls=True):
    """ Crawl a list of URLs specified in the input argument and return a
        list that contains one list of HTML documents for each URL in the input
        argument.

        :param urls: A list with all URLs to be crawled.
        :param max_depth: Maximum depth of crawling.
        :param max_links: Sets an upper bound on the number of links to crawl.
                          Default is None (no limit).
        :param cache_htmls: If True, the list of crawled HTMLs for each URL
                            is stored using the shelve module.
        :param shelve_db: Filename of the shelve db used for caching.
        :param append_htmls: If True, HTMLs are appended and returned as
            a list of lists (one for each URL in the input argument). Else,
            HTMLs are just stored in the database. Set this to False if the
            input URL list is large and one can run out of memory.

        :return: A list of lists containing raw HTMLs for each URL.

        Note: If `cache_htmls` is True, the cached HTMLs retrieved during an
              earlier crawl are loaded from the shelve-db, and hence params
              like `max_depth` will have no effect in the current crawl.

    """
    if cache_htmls:
        db = shelve.open(shelve_db)
    htmls = []
    for i, url in enumerate(urls):
        url = add_scheme(url)
        try:
            print 'Crawling webpage', i+1, len(urls), url
            if cache_htmls:
                if str(url) in db:
                    html = db[str(url)]
                else:
                    html = extract_html_rec(
                        url, max_depth=max_depth, max_links=max_links)
                    db[str(url)] = html
            else:
                html = extract_html_rec(
                    url, max_depth=max_depth, max_links=max_links)
            if append_htmls:
                htmls.append(html)
        except Exception, err:
            import traceback
            traceback.print_exc()
            print 'Exception', err
    if cache_htmls:
        db.close()
    return htmls
