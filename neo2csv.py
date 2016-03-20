from py2neo import authenticate, Graph, Node, Relationship
import csv, codecs, cStringIO

class Neo4jConfig(object):
    def __init__(self):
        self.protocol = "http"
        self.hostName = "localhost"
        self.portNumber = 7474
        self.dbPath = "/db/data/"
        self.useAuthentication = False
        self.userId = ""
        self.password = ""
        self.limit = 10 # limit = 0 means no limit, limit =n where n > 0 limits queries to at most n rows

    def host(self):
        return self.hostName + ":" + str(self.portNumber)

    def url(self):
        return self.protocol + "://" + self.host() + self.dbPath

# This is from http://stackoverflow.com/questions/5838605/python-dictwriter-writing-utf-8-encoded-csv-files :-)
class DictUnicodeWriter(object):

    def __init__(self, f, fieldnames, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.DictWriter(self.queue, fieldnames, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, D):
        self.writer.writerow(dict((k, v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in D.iteritems()))
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for D in rows:
            self.writerow(D)

    def writeheader(self):
        self.writer.writeheader()

class table(object):
    def __init__(self):
        self.columnHeadings = []
        self.rows = []

    def addRow(self, row):
        for col_name in row:
            if col_name not in self.columnHeadings:
                self.columnHeadings.append(col_name) # accumulate column headings for later output
        self.rows.append(row)

    def saveCsv(self, filename):
        fieldnames=[s.encode("utf-8") for s in self.columnHeadings]
        fieldnames.sort()
        with open(filename, 'wb') as csvfile:
            csvfile.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
            csvwriter = DictUnicodeWriter(csvfile, fieldnames)
            csvwriter.writeheader()
            csvwriter.writerows(self.rows)

### Start of code :-)

config = Neo4jConfig()

if config.useAuthentication:
    authenticate(config.host(), config.userId, config.password)

print "Connect to", config.url()
graph = Graph(config.url())
print "Connected:", graph.bound

relationshipTables = {} # one table for each of the relationship types for the current label

for label in graph.node_labels:
    print "Get nodes for label:", label

    currentTable = table()

    if config.limit > 0:
        print "*** Get Nodes with limit", config.limit
        nodes = graph.find(label, limit=config.limit)
    else:
        nodes = graph.find(label)

    for node in nodes:
        row = node.properties.copy()
        row["nodeId"] = node._id
        currentTable.addRow(row)

        # get relationships
        if config.limit > 0:
            # limit is for n relationships per node, so you may end up with n^2 relationships!
            nodeRelationships = graph.match(start_node=node, limit=config.limit)
        else:
            nodeRelationships = graph.match(start_node=node)


        for rel in nodeRelationships:
            relTableName = str(label + "_" + rel.type)
            print "\trelTableName", relTableName
            if relTableName in relationshipTables:
                relTable = relationshipTables[relTableName]
            else:
                relTable = table()
                relationshipTables[relTableName]=relTable

            relRows = rel.properties.copy()
            relRows["nodeId"] = node._id
            relRows["otherNodeId"] = rel.end_node._id

            relTable.addRow(relRows)

    tableCsvFileName = label + ".csv"
    print "Export label CSV", tableCsvFileName
    currentTable.saveCsv(tableCsvFileName)

for relTableName in relationshipTables:
    relTable = relationshipTables[relTableName]
    relTableCsvFileName = relTableName + ".csv"
    print "Export relationship CSV", relTableCsvFileName
    relTable.saveCsv(relTableCsvFileName)

print "Finished"
