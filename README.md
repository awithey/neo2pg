# neo2pg
I inteded this to write form Neo4j to PostgreSQL, but for now I'm content with output to CSV and then importing to PG.

neo2csv.py copy all Neo4j nodes and relationships to separate CSV files (one for each node label and relationship label).

This requires a [Neo4j](http://neo4j.com/download/) database.

### Dependancies:
py2neo
	pip install py2neo

## Usage:
neo2csv.py
 -? | --help {show this help}
 protocol=[http|https] {default=http}
 host=[neo4j hostname] {default=localhost
 port=[neo4j port number] {default=7474}
 db=[relative path to neo4j db] {default=/db/data
 userid=[neo4j user id {default=none}
 password=[passsword] {default=none}
 limit=[number: limit rows returned, 0 for all] {default=0}
 csvpath=[path to folder where CSV files are written] {default=.}