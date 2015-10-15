from cPickle import dump, load
import csv
import hashlib
import os
import os.path as osp


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    """ Helper function needed to read csv-files in utf-8. """
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


def get_md5(s):
    """ Return the md5 hash digest of the string argument. """
    m = hashlib.md5()
    m.update(s.encode('utf8'))
    return m.hexdigest()


class IoFs:
    """ Persistence class that uses the filesystem. """
    def __init__(self, basepath):
        self.basepath = osp.expanduser(basepath)
        self.cachepath = osp.join(self.basepath, 'cache')
        self.redirects = None
        self.errorurls = None
        self._setup_path()

    def _setup_path(self):
        if not os.path.exists(self.basepath):
            os.makedirs(self.basepath)
        if not os.path.exists(self.cachepath):
            os.makedirs(self.cachepath)

    def save_str(self, key, s):
        dump(s, open(osp.join(self.cachepath, get_md5(key)), 'w'))

    def load_str(self, key):
        filename = osp.join(self.cachepath, get_md5(key))
        if os.path.exists(filename):
            return load(open(filename))
        return None

    def _load_redirects(self):
        """ If the variable redirects is unset, load the dictionary from a
            csv-file.
        """
        if self.redirects is None:
            self.redirects = dict()
            redirectsfile = osp.join(self.basepath, 'redirects.csv')
            if os.path.exists(redirectsfile):
                reader = unicode_csv_reader(open(redirectsfile))
                self.redirects = dict((rows[0], rows[1]) for rows in reader)

    def add_redirect(self, url1, url2):
        """ Keep track of the http redirects so that we can properly update
            the base url needed to construct new urls with relative paths.
        """
        self._load_redirects()
        if (url1 != url2):
            self.redirects[url1] = url2
            redirectsfile = osp.join(self.basepath, 'redirects.csv')
            f = open(redirectsfile, 'a')
            csvout = csv.writer(f, delimiter=',', quotechar='"')
            csvout.writerow([url1.encode('UTF-8'), url2.encode('UTF-8')])
            f.close()

    def get_redirect(self, url):
        """ Return the redirect from a url stored by a previous call to
            `add_redirect`.
        """
        self._load_redirects()
        if url not in self.redirects:
            return url
        return self.redirects[url]

    def _load_error_urls(self):
        """ If the variable 'redirects' is unset, load the set from a csv-file.
        """
        if self.errorurls is None:
            self.errorurls = set()
            errorurlsfile = osp.join(self.basepath, 'errors.csv')
            if os.path.exists(errorurlsfile):
                reader = unicode_csv_reader(open(errorurlsfile))
                self.errorurls = set(rows[0] for rows in reader)

    def add_error_url(self, url):
        """ Keep track of the urls that return an error. """
        self._load_error_urls()
        if url not in self.errorurls:
            self.errorurls.add(url)
            errorurlsfile = osp.join(self.basepath, 'errors.csv')
            f = open(errorurlsfile, 'a')
            csvout = csv.writer(f, delimiter=',', quotechar='"')
            csvout.writerow([url.encode('UTF-8')])
            f.close()

    def is_error_url(self, url):
        """ Check if a url has returned some kind of error in the past. """
        self._load_error_urls()
        return url in self.errorurls
