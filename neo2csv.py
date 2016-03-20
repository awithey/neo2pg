from py2neo import authenticate, Graph, Node, Relationship

import sys, getopt, os
import csv, codecs, cStringIO

from py2neo.packages.httpstream import http

http.socket_timeout = 9999


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
                self.columnHeadings.append(col_name)  # accumulate column headings for later output
        self.rows.append(row)

    def saveCsv(self, path, filename):
        fieldnames = [s.encode("utf-8") for s in self.columnHeadings]
        fieldnames.sort()
        fullpath = os.path.join(path, filename)
        with open(fullpath, 'wb') as csvfile:
            print "\tWriting to", fullpath
            csvfile.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
            csvwriter = DictUnicodeWriter(csvfile, fieldnames)
            csvwriter.writeheader()
            csvwriter.writerows(self.rows)


def usage():
    print "Usage", sys.argv[0]
    print " -? | --help {show this help}"
    print " protocol=[http|https] {default=http}"
    print " host=[neo4j hostname] {default=localhost"
    print " port=[neo4j port number] {default=7474}"
    print " db=[relative path to neo4j db] {default=/db/data"
    print " userid=[neo4j user id {default=none}"
    print " password=[passsword] {default=none}"
    print " limit=[number: limit rows returned, 0 for all] {default=0}"
    print " csvpath=[path to folder where CSV files are written] {default=.}"
    print " nodelabels=[comma delimited list of node labels, get list from db if empty] {default=}"




def main():
    # Defaults
    protocol = "http"
    hostName = "localhost"
    portNumber = 7474
    dbPath = "/db/data/"
    userId = ""
    password = ""
    limit = 0  # limit = 0 means no limit, limit =n where n > 0 limits queries to at most n rows
    csvpath = "."
    nodeLabels = ""
    batchsize = 1000

    try:
        opts, args = getopt.getopt(sys.argv[1:], "?",
                                   ["help", "protocol=", "host=", "port=", "db=", "userid=", "password=", "limit=",
                                    "csvpath=", "nodelabels="])
    except getopt.GetoptError:
        print "ERROR unknown option!"
        print ""
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-?', '--help'):
            usage()
            sys.exit(0)
        elif opt == "--protocol":
            protocol = arg
        elif opt == "--host":
            hostName = arg
        elif opt == "--port":
            portNumber = arg
        elif opt == "--db":
            dbPath = arg
        elif opt == "--userid":
            userId = arg
        elif opt == "--password":
            password = arg
        elif opt == "--limit":
            limit = arg
        elif opt == "--csvpath":
            csvpath = arg
        elif opt == "--nodelabels":
            nodeLabels = arg
        else:
            print "ERROR: Unknown option", opt
            print ""
            usage()
            sys.exit(2)

    host = hostName + ":" + str(portNumber)
    url = protocol + "://" + host + dbPath

    print "Connect to", url

    if len(userId) > 0:
        authenticate(host, userId, password)

    graph = Graph(url)
    print "Connected:", graph.bound

    # Check if output directory exists
    if not os.path.isdir(csvpath):
        print "ERROR Directory doesn't exist", csvpath
        sys.exit(1)

    relationshipTables = {}  # one table for each of the relationship types for the current label

    if len(nodeLabels) > 0:
        labels = nodeLabels.split(',')
    else:
        labels = graph.node_labels  # Get list of labels from the database

    for label in labels:
        print "Get nodes for label:", label

        currentTable = table()

        nodecount=0

        while True:
            matchLimit = batchsize
            if limit > 0:
                if nodecount < limit:
                    if nodecount + batchsize > limit:
                        matchLimit = limit - nodecount
                else:
                    break

            # nodes = graph.find(label)
            nodes = graph.cypher.stream("MATCH (n:" + str(label) + ") RETURN n ORDER BY id(n) SKIP {skip} LIMIT {limit}", {"skip": nodecount, "limit": matchLimit})

            if not nodes:
                break

            for g_node in nodes:
                nodecount += 1
                node = g_node.n
                row = node.properties.copy()
                row["nodeId"] = node._id
                currentTable.addRow(row)

                # get relationships
                if limit > 0:
                    # limit is for n relationships per node, so you may end up with n^2 relationships!
                    nodeRelationships = graph.match(start_node=node, limit=limit)
                else:
                    nodeRelationships = graph.match(start_node=node)

                for rel in nodeRelationships:
                    relTableName = str(label + "_" + rel.type)

                    if relTableName in relationshipTables:
                        relTable = relationshipTables[relTableName]
                    else:
                        relTable = table()
                        relationshipTables[relTableName] = relTable

                    relRows = rel.properties.copy()
                    relRows["nodeId"] = node._id
                    relRows["otherNodeId"] = rel.end_node._id

                    relTable.addRow(relRows)
            print "\tNode count", nodecount

        tableCsvFileName = label + ".csv"
        print "Export label CSV", tableCsvFileName
        currentTable.saveCsv(csvpath, tableCsvFileName)

    for relTableName in relationshipTables:
        relTable = relationshipTables[relTableName]
        relTableCsvFileName = relTableName + ".csv"
        print "Export relationship CSV", relTableCsvFileName
        relTable.saveCsv(csvpath, relTableCsvFileName)

    print "Finished"


if __name__ == "__main__":
    main()
