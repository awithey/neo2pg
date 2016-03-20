# neo2pg
I inteded this to write form Neo4j to PostgreSQL, but for now I'm content with output to CSV and then importing to PG.

neo2csv.py copy all Neo4j nodes and relationships to separate CSV files (one for each node label and relationship label).

This requires a [Neo4j](http://neo4j.com/download/) database.

Dependancies:
py2neo
	pip install py2neo

Usage:
    Edit neo2csv.py, add relavant config values (TODO: Make these parameters :-)
    run neo2csv.py