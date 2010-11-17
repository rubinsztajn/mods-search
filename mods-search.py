import web, apsw

urls = (
    '/', 'Index',
    '/(.+?)', 'Record'
    )

app = web.application(urls, globals())
render = web.template.render('templates/')
conn = apsw.Connection('//umalstf2/spec_collections/aaron/db/mods.db')
c = conn.cursor()

class Index:
    def GET(self):
        
        i = web.input()
        q = i.get('q')
        f = i.get('field')
        results = None

        if q:
            if f == 'full':
                rows = c.execute("select record_id, title, creator from fulltext where full match ?", (q,))
            elif f == 'title':
                rows = c.execute("select record_id, title, creator from fulltext where title match ?", (q,))
            elif f == 'creator':
                rows = c.execute("select record_id, title, creator from fulltext where creator match ?", (q,))
            elif f == 'names':
                rows = c.execute("select record_id, title, creator from fulltext where names match ?", (q,))
            elif f == 'abs':
                rows = c.execute("select record_id, title, creator from fulltext where abs match ?", (q,))
            results = rows.fetchall()

        return render.index(results, q)
        
class Record:
    def GET(self, id):
        row = c.execute("select full from fulltext where record_id match ?", (id,))
        result = row.fetchall()
        record = result[0][0]
        web.header('Content-Type', 'text/xml')
        return render.record(record)


if __name__ == "__main__": app.run()
