#!/bin/bash

# Install essential packages from Apt
apt-get update -y


apt-get -q -y install mysql-server

mysqladmin -u root password 12345

sed -i 's/symbolic-links=0/symbolic-links=0\nbind-address=0.0.0.0/g' /etc/mysql/my.cnf

mysql -uroot -p12345 -e "create database debatovani;GRANT ALL PRIVILEGES ON debatovani.* TO debatovani@localhost IDENTIFIED BY '12345';FLUSH PRIVILEGES;"

mysql -u debatovani -p12345 -h localhost debatovani < /vagrant/data.sql

service mysql restart