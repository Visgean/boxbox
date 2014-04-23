Exec { path => [ "/bin/", "/sbin/" , "/usr/bin/", "/usr/sbin/" ] }

class { 'puppi': }
class { 'stdlib': }

exec { 'apt-get update':
  command => 'apt-get update',
  timeout => 60,
  tries   => 3
}


class { 'apt':
  always_apt_update    => true,
}



class { "mysql":
  root_password => '12345',
}

mysql::grant { 'debatovani':
  mysql_privileges => 'ALL',
  mysql_password => '12345',
  mysql_db => 'debatovani',
  mysql_user => 'debatovani',
  mysql_host => 'host',
  mysql_db_init_query_file => '/vagrant/data.sql',
}