import numpy as np
from crawler.crawl import crawl_urls
from crawler.text_extraction import extract_texts


class RestaurantClassifier(object):

    def __init__(self, classifier, text_params=None, label_names=None):
        """ The restaurant classifier class.

            :param classifier: A trained scikit-learn classifier that
                takes documents as input.
            :param text_params: A dictionary containing the parameters that
                specify text extraction behaviour. Should be the same as used
                during classifier training. If None, `default_text_params` is
                used.
            :param label_names: A list with label names, where the index
                corresponds to the respective label ID (optional).
        """
        self.classifier = classifier
        self.text_params = (text_params if text_params is not None else
                            self.default_text_params())
        self.label_names = (label_names if label_names is not None else
                            self.classifier.classes_)

    def default_text_params(self):
        """ Default parameters to using during text extraction. """
        return {'use_stemmer': True, 'title_weight': 2, 'max_links': 99,
                'header_weights': [3, 3, 2, 2, 1, 1], 'homepage_weight': 2,
                'ukkonen_len': 0, 'use_pdf': True, 'max_depth': 4}

    def get_htmls(self, urls):
        """ Crawl URL(s) and return HTML(s). """
        return crawl_urls(urls, max_depth=self.text_params['max_depth'],
                          max_links=self.text_params['max_links'])

    def htmls2docs(self, htmls):
        """ Convert HTMLs to text documents using the params specified in
            `text_params`.
        """
        docs = []
        for i, html in enumerate(htmls):
            doc = extract_texts(
                html,
                title_weight=self.text_params['title_weight'],
                header_weights=self.text_params['header_weights'],
                use_pdf=self.text_params['use_pdf'],
                use_stemmer=self.text_params['use_stemmer'],
                ukkonen_len=self.text_params['ukkonen_len'],
                homepage_weight=self.text_params['homepage_weight'])
            docs.append(' '.join(doc))
        return docs

    def predict(self, urls, proba=True):
        """ Given a URL (or list of URLs), predict the restaurant cuisine.
            If `proba` is True, the three most probable labels are return along
            with their respective probability.
        """
        if isinstance(urls, str):
            urls = [urls]
        htmls = self.get_htmls(urls)
        docs = self.htmls2docs(htmls)
        if proba:
            scores = self.classifier.predict_proba(docs)
            for i in xrange(scores.shape[0]):
                sc = scores[i, :]
                idx = np.argsort(sc)[::-1]
                sorted_scores = sc[idx]
            return [(self.label_names[idx[0]], sorted_scores[0]),
                    (self.label_names[idx[1]], sorted_scores[1]),
                    (self.label_names[idx[2]], sorted_scores[2])]
        return self.classifier.predict(docs)
