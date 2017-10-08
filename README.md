# Project-SQL-for-Git

## Links
Original osm dataset
https://www.openstreetmap.org/export#map=12/1.3450/103.8500

## Repository contents
```audit.py```
Launch the audit scripts to explore the dataset

```load.py```
Extract the data from the osm dataset
Transform the extracted dataset (by calling transform.py)
Load the transformed dataset into csv files

```project_report.md```
Narrative report explaining the steps of the data wrangling set

```schema.py```
List the schema for the load.py scripts

```take_sample.py```
Extract a subset of the initial osm dataset

```transform.py```
Transform incorrect entries into correct entries

```data\schema.sql```
SQL queries used to create the sqlite3 database

```data\osm\singapore-shorter.osm```
Subset of the initial osm dataset
