## Define Package List for CentOS6
$nosedepscent6 = [ "gcc", "python-devel", "python-httplib2", "python-setuptools" ]

## Define Package List for SLES 11
$nosedepssles11 = [ "gcc", "python-devel", "python-httplib2", "python-distribute" ]

## Process deps for Cent5
if ($::osfamily == 'RedHat'and $::operatingsystemrelease =~ /^5/) {
  package { $nosedepscent5: ensure => installed }
} elsif
## Process deps for Cent6
($::osfamily == 'RedHat'and $::operatingsystemrelease =~ /^6/) {
  package { $nosedepscent6: ensure => installed }
} else {
## Process deps for SLES 11 SP2
  package { $nosedepssles11: ensure => installed }
}

## Install the nose framework
## CentOS 5
if ($::osfamily == 'RedHat'and $::operatingsystemrelease =~ /^5/) {
  package { "python26-nose":
  ensure => installed,
  require => Package[$nosedepscent5],
  }
## CentOS 6
} elsif $::osfamily == 'RedHat' and $::operatingsystemrelease =~ /^6/ {
  exec { "easy_install_nose":
  command => "/usr/bin/easy_install-2.6 nose",
  require => Package[$nosedepscent6],
  creates => "/usr/bin/nosetests",
}
} else {
## Assume SLES 11
exec { "install_nose_sles":
  command => "/usr/bin/zypper --no-gpg-checks install -y http://download.opensuse.org/repositories/devel:/languages:/python/SLE_11_SP3/x86_64/python-nose-1.3.0-66.1.x86_64.rpm",
  require => Package[$nosedepssles11],
  creates => "/usr/bin/nosetests",
 }

}

