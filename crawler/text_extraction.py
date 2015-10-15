# -*- coding: utf-8 -*-
""" Module containing functionality for extracting text from HTML files. """

import re
import string
import StringIO
from unidecode import unidecode

from bs4 import BeautifulSoup
import langdetect
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import GermanStemmer
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams

from crawler.text_utils import split_camel_case, str2unicode


def replace_umlaute(text):
    """ Replace German Umlaute. """
    rep = {u'Ä': 'Ae', u'ä': 'ae',
           u'Ö': 'Oe', u'ö': 'oe',
           u'Ü': 'Ue', u'ü': 'ue'}
    for k, v in rep.iteritems():
        text = text.replace(k, v)
    return text


def clean_text(text):
    """ Clean unicode text by replacing German Umlaute first, and then
        converting it to ascii using `unidecode`.
    """
    # Convert German Umlaute
    text = replace_umlaute(text)
    # Convert to ASCII
    return unidecode(text)


def is_pdf(s):
    """ Check if a binary string is a pdf file based on the magic number. """
    if len(s) < 4:
        return False
    return s[:4] == '%PDF'


def apply_stemmer(doc):
    """ Apply a word stemmer to the input document. First, language detection is
        performed and the corresponding stemmer applied (English and German
        supported).
    """
    try:
        lang = langdetect.detect(doc)
    except Exception:
        return doc
    stemmer = None
    if lang == 'en':
        stemmer = PorterStemmer()
    if lang == 'de':
        stemmer = GermanStemmer()
    if stemmer is None:
        return doc
    return ' '.join([stemmer.stem(w) for w in doc.split(' ')])


def remove_repeated_long_strings(l, minlen=1000):
    """ Remove duplicated long strings efficiently using the Ukkonen algorithm.
        The function recursively removes repeated strings as long as they are
        longer than `minlen`.

        Note: If the longest string overlaps with its repeated counterpart,
              it is not removed and the algorithm returns.
    """
    import ukkonen
    l = ' ' + l + ' '
    s = ukkonen.getLongestRepeatedSubstring(l + '$')
    while len(s) > minlen:
        while s[0] != ' ':
            s = s[1:]
        while s[-1] != ' ':
            s = s[:-1]
        if l.count(s) == 1:
            return l.strip()
        l = l.replace(s, ' ')
        l = l + s
        l = l.replace('  ', ' ')
        s = ukkonen.getLongestRepeatedSubstring(l + '$')
    return l.strip()


def is_visible_elem(elem):
    """ Return True, if the input html text is visible on the website. """
    if elem.parent.name in ['style', 'script', '[document]', 'head']:
        return False
    elif re.match('<!--.*-->', str(elem.encode('utf-8'))):
        return False
    return True


def extract_text_pdf(s):
    """ Extracts text from a PDF. """
    fp = StringIO.StringIO()
    outfp = StringIO.StringIO()
    fp.write(s)
    laparams = LAParams()
    imagewriter = None
    pagenos = set()
    caching = True
    rsrcmgr = PDFResourceManager(caching=caching)
    maxpages = 0
    rotation = 0
    password = ''
    device = TextConverter(
        rsrcmgr, outfp,
        laparams=laparams, imagewriter=imagewriter)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.get_pages(fp, pagenos,
                                  maxpages=maxpages, password=password,
                                  caching=caching, check_extractable=True):
        page.rotate = (page.rotate+rotation) % 360
        interpreter.process_page(page)
    fp.close()
    return str2unicode(outfp.getvalue())


def extract_text_html(html, title_weight=None, header_weights=None):
    """ Extracts text from an HTML. """
    soup = BeautifulSoup(html)
    # Extract visible text from soup
    texts = soup.findAll(text=True)
    text = ' '.join(filter(is_visible_elem, texts))
    # Add more weight to the title
    if title_weight:
        if soup.title is not None and soup.title.string is not None:
            text = text + ' ' + ' '.join(
                [soup.title.string] * (title_weight-1))
    # Add more weight to the headers
    if header_weights:
        for i in xrange(6):
            text = text + ' ' + ' '.join(
                [' '.join([elem.getText() for elem in soup.findAll(
                    'h' + str(i+1))])] * header_weights[i])
    return text


def extract_text(doc, title_weight=None, header_weights=None, use_pdf=True,
                 use_stemmer=False, ukkonen_len=0):
    """ Extracts cleaned text from an HTML or PDF. """
    if is_pdf(doc):
        if use_pdf:
            try:
                text = extract_text_pdf(doc)
            except:
                # TODO: Nice error handling
                return ''
        else:
            return ''
    else:
        text = extract_text_html(
            str2unicode(doc),
            title_weight=title_weight,
            header_weights=header_weights)
    # Replace newlines etc.
    text = re.sub('\s+', ' ', text)
    # Replace Umlaute and apply 'unidecode'
    text = clean_text(text)
    # Remove punctuation
    replace_punctuation = string.maketrans(
        string.punctuation, ' ' * len(string.punctuation))
    text = text.translate(replace_punctuation)
    # Remove multiple spaces
    text = re.sub(' +', ' ', text)
    # Strip
    text = text.strip()
    # Split camel case words
    text = ' '.join([split_camel_case(word) for word in text.split(' ')])
    # Remove digits
    text = ''.join([c for c in text if not c.isdigit()])
    # Remove single characters
    text = ' '.join([word for word in text.split(' ') if len(word) > 1])
    # Remove multiple spaces
    text = re.sub(' +', ' ', text)
    # Stem
    if use_stemmer:
        text = apply_stemmer(text)
    # Remove long repeated strings
    if ukkonen_len:
        text = remove_repeated_long_strings(text, ukkonen_len)
    return text.lower()


def extract_texts(htmls, title_weight=None, header_weights=None, use_pdf=True,
                  use_stemmer=False, ukkonen_len=0, hp_weight=1):
    """ Extract cleaned text from a list of HTMLs. """
    docs = [extract_text(
            html, title_weight, header_weights, use_pdf, use_stemmer,
            ukkonen_len) for html in htmls]
    if docs and hp_weight > 1:
        docs.extend([docs[0]] * (hp_weight - 1))
    return docs
