from nose.tools import eq_
from crawler.text_utils import split_camel_case


def test_split_camel_case():
    eq_(split_camel_case('BlaBla'), 'Bla Bla')
    eq_(split_camel_case('Bla'), 'Bla')
    eq_(split_camel_case('iBla'), 'iBla')
    eq_(split_camel_case('iBlaBla'), 'iBla Bla')
    eq_(split_camel_case('BlaBlaBlaaa'), 'Bla Bla Blaaa')
    eq_(split_camel_case('iBlaBla BlaaaBla'), 'iBla Bla  Blaaa Bla')
