boxbox
======

Greybox ( http://debatovani.cz/greybox/ ) analysis

Place your sql data into git root as 'data.sql'. Install rethinkdb.

```bash
cd vagrant/
vagrant up
vagrant ssh

cd ..

rethinkdb

python export/greybox_export.py

```
