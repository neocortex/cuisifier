import rethinkdb as r


class IoRethinkdb:
    """ Persistence class that uses RethinkDB. """
    def __init__(self, host, port):
        self.conn = r.connect(host, port).repl()
        if 'resmio' not in r.db_list().run(self.conn):
            r.db_create('resmio').run(self.conn)
            self.conn.use('resmio')
            r.table_create('binary').run(self.conn)
            r.table_create('redirects').run(self.conn)
            r.table_create('errors').run(self.conn)
            r.table('binary').index_create('key').run(self.conn)
        self.conn.use('resmio')

    def save_str(self, key, value):
        r.table('binary').insert(
            {'key': key, 'value': r.binary(value)}).run(self.conn)

    def load_str(self, key):
        for v in r.table('binary').get_all(
                key, index='key').pluck('value').run(self.conn):
            return v['value']
        return None

    def add_redirect(self, url1, url2):
        r.table('redirects').insert(
            {'url1': url1, 'url2': url2}).run(self.conn)

    def get_redirect(self, url1):
        for v in r.table('redirects').filter(
                {'url1': url1}).pluck('url2').run(self.conn):
            return v['url2']
        return url1

    def add_error_url(self, url1):
        """ Keeps track of the URLs that return an error. """
        r.table('errors').insert({'url1': url1}).run(self.conn)

    def is_error_url(self, url1):
        """ Check if a URL has returned some an error in the past. """
        for v in r.table('errors').filter({'url1': url1}).run(self.conn):
            return True
        return False
