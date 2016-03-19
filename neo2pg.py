from py2neo import authenticate, Graph, Path, Node, Relationship

class Neo4jConfig(object):
    def __init__(self):
        self.protocol = "http"
        self.hostName = "localhost"
        self.portNumber = 7474
        self.dbPath = "/db/data/"
        self.useAuthentication = False
        self.userId = ""
        self.password = ""

    def host(self):
        return self.hostName + ":" + str(self.portNumber)

    def url(self):
        return self.protocol + "://" + self.host() + self.dbPath

class table(object):
    def __init__(self):
        self.columnHeadings = []
        self.rows = []

    def addRow(self, newRow):
        for col_name in newRow:
            if col_name not in self.columnHeadings:
                self.columnHeadings.append(col_name) # accumulate column headings for later output
        self.rows.append(newRow)

### Start of code :-)

config = Neo4jConfig()

if config.useAuthentication:
    authenticate(config.host(), config.userId, config.password)

print "Connect to", config.url()
graph = Graph(config.url())
print "Connected:", graph.bound

relationshipTables = dict # one table for each of the relationship types for the current label

for label in graph.node_labels:
    print "Label:", label

    currentTable = table()

    print "Get nodes *** LIMIT 3 ***"
    nodes = graph.find(label, limit=3)

    for node in nodes:
        currentTable.addRow(node.properties)

        # get relationships
        print "Get relationships *** LIMIT 3 ***"
        nodeRelationships = graph.match(start_node=node, limit=3)

        for rel in nodeRelationships:
            relTableName = label + "_" + rel.end_node.label
            if relTableName in relationshipTables:
                relTable = relationshipTables[relTableName]
            else:
                relTable = table()

            relTable.addRow(rel.properties)
