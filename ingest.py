import apsw, os, glob, sys, fnmatch, time
from lxml import etree
from optparse import OptionParser

usage = "usage: %prog [options] arg1"
parser = OptionParser(usage=usage)

# Set options
parser.add_option("-a", "--add-only", action="store_true", dest="add")
parser.add_option("-u", "--add-and-update", action="store_true", dest="update")
 
(options, args) = parser.parse_args()

ns = {'mods':'http://www.loc.gov/mods/v3'}

conn = apsw.Connection('r:/aaron/db/mods.db')
c = conn.cursor()
i = 0
u = 0

def name2text(names):
    if len(names) == 1:
        fullname = names[0].text
    elif len(names) > 1:
        fullname = names[0].text + ', ' + names[1].text
    else: 
        fullname = ''

    return fullname


print time.strftime("%Y-%m-%d")

for path, dirs, files in os.walk(args[0]):
    for filename in files:
        if (fnmatch.fnmatch(filename, '*.xml')) and (filename[18:21] != 'tei'):
            filepath = os.path.join(path, filename)
            stats = os.stat(filepath)
            modtime = time.strftime("%Y%m%d:%H:%m:%S", time.localtime(stats.st_mtime))
            id, ext = os.path.splitext(filename)
            print "Checking:", id
            result = c.execute("select record_id, lastmod from fulltext where record_id match ?", (id,))
            r = result.fetchall()
            if r:
                if r[0][1] != modtime:
                    r = 'update'
                
            if not r or r == 'update':
                
                tree = etree.parse(filepath)
                full = etree.tostring(tree, pretty_print=True)
                title = tree.xpath('//mods:titleInfo/mods:title', namespaces=ns)
                creator = tree.xpath('//mods:roleTerm[text()="creator"]', namespaces=ns)
                creatorname = ''
                othernames = ''
                if creator:
                    name = creator[0].getparent().getparent()
                    creatorname = name2text(name)
        
                names = tree.xpath('//mods:name', namespaces=ns)

                if names:
                    for name in names:
                        othernames += name2text(name) + ' '
        
                abstract = tree.xpath('//mods:abstract', namespaces=ns)

                if title:
                    t = title[0].text
                else: 
                    t = ''
        
                if abstract:
                    a = abstract[0].text
                else:
                    a = ''

                values = (id, modtime, t, creatorname, othernames, a, full)
                if (r == 'update') and (options.update) :
                    c.execute("update fulltext set lastmod=? where record_id=?", (values[1], values[0]))
                    c.execute("update fulltext set title=? where record_id=?", (values[2], values[0]))
                    c.execute("update fulltext set creator=? where record_id=?", (values[3], values[0]))
                    c.execute("update fulltext set names=? where record_id=?", (values[4], values[0]))
                    c.execute("update fulltext set abs=? where record_id=?", (values[5], values[0]))
                    c.execute("update fulltext set full=? where record_id=?", (values[6], values[0]))
                    print "Updated:", values[0]
                    u += 1
                elif (r != 'update') and (options.add or options.update):
                    c.execute('insert into fulltext values (?,?,?,?,?,?,?)', values)
                    print "Added:", values[0]
                    i += 1

print ''
print i, "total records added to the database"
print u, "total records updated"
        


