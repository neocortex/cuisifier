import ukkonen


def get_longest_repeated_substring_brute(s):
    maxlen = 0
    maxs = ''
    for i in range(len(s)):
        for j in range(i+1, len(s)+1):
            for ii in range(len(s)):
                for jj in range(ii+1, len(s)+1):
                    if i != ii and j != jj and s[i:j] == s[ii:jj]:
                        if maxlen < len(s[i:j]):
                            maxlen = len(s[i:j])
                            maxs = s[i:j]
    return maxs


def check(s):
    assert get_longest_repeated_substring_brute(s) == \
        ukkonen.getLongestRepeatedSubstring(s+'$')


def test_ukkonen_library():
    check('GEEKSFORGEEKS')
    check('AAAAAAAAAA')
    check('ABCDEFG')
    check('ABABABA')
    check('ATCGATCGA')
    check('banana')
    check('abcpqrabpqpq')
