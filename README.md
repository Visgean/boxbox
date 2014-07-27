export
======

*Note: you can just load dumped data that are in upper directory.*


Place your sql data into git root as 'data.sql'. Install rethinkdb.


```bash
cd vagrant/
vagrant up
vagrant ssh

cd ..

rethinkdb

python greybox_export.py

```
