Exec { path => [ "/bin/", "/sbin/" , "/usr/bin/", "/usr/sbin/" ] }

exec { 'apt-get update':
  command => 'apt-get update',
  timeout => 60,
  tries   => 3
}

class { 'apt':
  always_apt_update => true,
}

package { ['python-software-properties']:
  ensure  => 'installed',
  require => Exec['apt-get update'],
}

$sysPackages = [ 'build-essential', 'git', 'curl']
package { $sysPackages:
  ensure => "installed",
  require => Exec['apt-get update'],
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