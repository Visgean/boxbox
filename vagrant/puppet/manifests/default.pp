Exec { path => [ "/bin/", "/sbin/" , "/usr/bin/", "/usr/sbin/" ] }

class { 'puppi': }
class { 'stdlib': }


class { "mysql":
  root_password => '12345',
}

mysql::grant { 'debatovani':
  mysql_privileges => 'ALL',
  mysql_password => '12345',
  mysql_db => 'debatovani',
  mysql_user => 'debatovani',
  mysql_host => 'host',
}

exec { 'greybox import':
  command => 'mysql -u root --password=12345 debatovani < /vagrant/data.sql',
}