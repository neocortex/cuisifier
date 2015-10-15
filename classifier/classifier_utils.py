""" Module with some util functions for restaurant classifier data
    processing.
"""
import shelve

from crawler import crawl, text_extraction


def map_labels(labels):
    """ Map the labels to numeric ids. Return a list with unique labels,
        in which the list index is the corresponding label id.

    """
    label_ids = []
    id_to_label = []
    for label in labels:
        if label not in id_to_label:
            id_to_label.append(label)
        label_ids.append(id_to_label.index(label))
    return label_ids, id_to_label


def urls_to_htmls(urls, text_params):
    """ Given a list of urls and a dictionary with the text preprocessing
        parameters, return a list of extracted html for each url.

    """
    return crawl.crawl_urls(
        urls, max_depth=text_params['max_depth'],
        max_links=text_params['max_links'],
        cache_htmls=text_params['cache_htmls'],
        append_htmls=text_params['append_htmls'],
        shelve_db=text_params['shelve_db'])


def htmls_to_docs(urls, htmls, text_params):
    """ Given a list of urls and a dictionary with text preprocessing
        parameters, return a list of extracted text for each html using.

    """
    docs = []
    if text_params['cache_docs']:
        db = shelve.open(text_params['docs_shelve'])
    for url, html in zip(urls, htmls):
        if text_params['cache_docs']:
            if str(url) in db:
                docs.append(db[str(url)])
            else:
                doc = text_extraction.extract_texts(
                    html,
                    title_weight=text_params['title_weight'],
                    header_weights=text_params['header_weights'],
                    use_pdf=text_params['use_pdf'],
                    use_stmmer=text_params['use_stemmer'],
                    ukkonen_len=text_params['ukkonen_len'],
                    homepage_weight=text_params['homepage_weight'])
                doc = ' '.join(doc)
                docs.append(doc)
                db[str(url)] = doc
    if text_params['cache_docs']:
        db.close()
    return docs


def urls_to_docs(urls, text_params):
    """ Given a list of urls and a dictionary with text preprocessing
        rules, return a list of extracted documents for each url.

    """
    htmls = urls_to_htmls(urls, text_params=text_params)
    return htmls_to_docs(urls, htmls, text_params=text_params)
