from crawler.crawl_resmio import filter_urls_from_platforms


def test_filter_urls_from_platforms():
    bad_strings = [
        'https://www.facebook.com/Uoksas',
        u'https://plus.google.com/103185425957074519771/about?gl=de&hl=en',
        u'http://www.restaurant-kritik.de/24344',
        u'http://www.variete.de/de/spielorte/hannover/hannover.html',
        u'http://www.speisekarte.de/l%C3%BCneburg/restaurant/'
        'la_taverna_italienisches_restaurant/tischreservierung',
        u'http://www.yelp.de/biz/kashmir-berlin',
        u'https://de-de.facebook.com/Sonvery']

    good_strings = [
        'http://www.something.com/facebook',
        'http://www.something.com/google/bla',
        'http://www.something.com/speisekarte/drinks',
        'http://www.something.com/facebook/variete']

    for url in bad_strings:
        assert not filter_urls_from_platforms(bad_strings)
    for url in good_strings:
        assert (len(filter_urls_from_platforms(good_strings)) ==
                len(good_strings))
