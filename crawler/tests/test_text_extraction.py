# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from nose.tools import eq_

from crawler.text_extraction import replace_umlaute


def test_convert_umlaute():
    text_in = (u'Die süße Hündin läuft in die Höhle des Bären, der sie '
               u'zum Teekränzchen eingeladen hat, da sie seine drei schönen '
               u'Krönchen gerettet hat, was sie wie folgt angestellt hat: Sie '
               u'läuft über einen Fluss und tötet alle grünen Frösche, die '
               u'über die Krönchen wachen, so hat sie diese schönen Krönchen '
               u'gerettet. Überreaschung, Änderungen, und Österreich.')
    text_out = (u'Die sue\xdfe Huendin laeuft in die Hoehle des Baeren, der'
                u' sie zum Teekraenzchen eingeladen hat, da sie seine drei'
                u' schoenen Kroenchen gerettet hat, was sie wie folgt'
                u' angestellt hat: Sie laeuft ueber einen Fluss und toetet'
                u' alle gruenen Froesche, die ueber die Kroenchen wachen,'
                u' so hat sie diese schoenen Kroenchen gerettet.'
                u' Ueberreaschung, Aenderungen, und Oesterreich.')
    eq_(replace_umlaute(text_in), text_out)


def test_separate_words_between_tags():
    html = '<p>Luke,</p>I am<b>your</b>father.'
    out = 'Luke, I am your father.'
    soup = BeautifulSoup(html)
    text = soup.get_text(separator=' ')
    eq_(text, out)
