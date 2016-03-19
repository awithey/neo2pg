from py2neo import authenticate, Graph, Path, Node, Relationship

#authenticate("localhost:7474", "user", "password")

neo_uri = "http://localhost:7474/db/data/"
print "Connect to", neo_uri
graph = Graph(neo_uri)
print "Connected:", graph.bound

for label in graph.node_labels:
    print "Label:", label

    print "Get nodes *** LIMIT 2 ***"
    nodes = graph.find(label,limit=2)

    for node in nodes:
        print "\tNode:", node

        for node_prop in node.properties:
            node_value = node.properties[node_prop]
            print "\t\tProperty:", node_prop, "=", node_value

        print "Getting relationships *** LIMIT 10 ***"
        relationships = graph.match(start_node=node,limit=10)

        for rel in relationships:
            print "\t\t\tRelated node:", rel.end_node
            for rel_prop in rel.properties:
                print "\t\t\t\tProperty:", rel_prop, "=", rel.properties[rel_prop]