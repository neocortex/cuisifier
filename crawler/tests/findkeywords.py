import csv
import os
from crawler import crawl, text_extraction


def __test_site_kw(url, kws):
    if len(kws) > 0:
        html = crawl.extract_html_rec(url, max_depth=4)
        txt = text_extraction.extract_texts(html)
        txts = ' '.join(txt)

        failed = False
        for kw in kws:
            if txts.find(text_extraction.clean_text(kw).lower()) == -1:
                print 'error, keyword not found in txt', url, kw
                failed = True
        if not failed:
            print 'OK', url


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


def test_key_finder():
    filename = os.path.dirname(os.path.abspath(__file__)) + '/findkeywords.csv'
    reader = unicode_csv_reader(open(filename))
    for row in reader:
        __test_site_kw(row[0], row[1:])

if __name__ == '__main__':
    test_key_finder()
