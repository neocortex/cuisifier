from crawler import crawl


def test_filter_url():
    # filter out
    assert crawl.filter_url(
        'http://host/', 'http://host2/index.html')
    assert crawl.filter_url(
        'http://host/', 'http://host/a.jpg')
    assert crawl.filter_url(
        'http://host/', 'http://host/a.jpeg')
    assert crawl.filter_url(
        'http://host/', 'http://host/a.JPEG')
    assert crawl.filter_url(
        'http://host/', 'http://host/a.JPEG?a=1')
    assert crawl.filter_url(
        'http://host/', 'http://host/a.png')
    assert crawl.filter_url(
        'http://host/', 'http://host/a.gif')
    assert crawl.filter_url(
        'http://host/', 'http://host/a.otherextension')
    assert crawl.filter_url(
        'http://host/', 'mailto:a@a.es')
    assert crawl.filter_url(
        'calendar://host/', 'calendar://host/')
    assert crawl.filter_url(
        'http://host/', '')
    assert crawl.filter_url(
        'http://host/', '#anchor')
    assert crawl.filter_url(
        'http://host/', 'http://host/index.php?img=a.jpg')
    assert crawl.filter_url(
        'noschema', 'noschema')
    # filter in
    assert not crawl.filter_url(
        'http://host/slkddskljee', 'http://host/slkddskljee')
    assert not crawl.filter_url(
        'http://host/', 'http://host/index.php')
    assert not crawl.filter_url(
        'http://host/', 'http://host/index.php?a=1&b=2')
    assert not crawl.filter_url(
        'http://host/', 'http://host/index.html')
    assert not crawl.filter_url(
        'http://host/', 'http://host/index.htm')
    assert not crawl.filter_url(
        'http://host/', 'http://host/index.shtm')
    assert not crawl.filter_url(
        'http://host/', 'http://host/index.shtml')
    assert not crawl.filter_url(
        'http://host/', 'http://host/index.php')
    assert not crawl.filter_url(
        'http://host/', 'http://host/index.jsp')
    assert not crawl.filter_url(
        'http://host/', 'http://host/index.aspx')
    assert not crawl.filter_url(
        'http://host/', 'http://host/index.asp')
    assert not crawl.filter_url(
        'http://host/', 'http://host/folder')
    assert not crawl.filter_url(
        'http://host/', 'http://host/folder/another-folder')
