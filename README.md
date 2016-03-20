# neo2pg
I inteded this to write form Neo4j to PostgreSQL, but for now I'm content with output to CSV and then importing to PG.

neo2csv.py copy all Neo4j nodes and relationships to separate CSV files (one for each node label and relationship label).

This requires a [Neo4j](http://neo4j.com/download/) database.

### Dependancies:
*py2neo<br/>
&nbsp; pip install py2neo

## Usage:
neo2csv.py<br/>
&nbsp; -? | --help {show the help}<br/>
&nbsp; protocol=[http|https] {default=http}<br/>
&nbsp; host=[neo4j hostname] {default=localhost<br/>
&nbsp; port=[neo4j port number] {default=7474}<br/>
&nbsp; db=[relative path to neo4j db] {default=/db/data<br/>
&nbsp; userid=[neo4j user id {default=none}<br/>
&nbsp; password=[passsword] {default=none}<br/>
&nbsp; limit=[number: limit rows returned, 0 for all] {default=0}<br/>
&nbsp; csvpath=[path to folder where CSV files are written] {default=.}<br />
&nbsp; nodelabels=[comma delimted list of node lables, reads list form db if empty] {default=.}