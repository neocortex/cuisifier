""" Useful functions for text manipulation. """

import re


def split_camel_case(text):
    """ Split a string in CamelCase if both resulting strings are longer than
        a single character.

    """
    new_text = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', text)
    new_text = re.sub('([a-z0-9])([A-Z])', r'\1 \2', new_text)
    words = new_text.split(' ')
    if len(words) > 1:
        if len(words[0]) != 1:
            return new_text
        elif len(words) > 2:
            return ' '.join([''.join(words[:2]), ' '.join(words[2:])])
    return text


def str2unicode(s):
    """ Convert a str into unicode using utf-8 first, and latin-1 if utf-8
        fails.
    """
    try:
        return unicode(s, encoding='utf-8')
    except Exception:
        return unicode(s, encoding='latin-1')
