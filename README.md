# Torque Tests
This repository holds all system level tests for torque.

The tests are in the torque folder, and the `ace` folder
stores common classes and utilities to be shared across tests.

# Requirements

* Python 2.6
* nose 1.3

# How to Run

```
# Run level 1 tests
nosetests-2.6 -a level=1 -v -s
# Run level 2 tests
nosetests-2.6 -a level=2 -v -s
```

# Levels

* Level 1: Short run tests (5 minutes total for all tests), could also be termed "Smoke tests"
* Level 2: Longer running, more intensive, more specific tests
* Level 3: Largely undefined, ideas are performance tests, environment specific tests, etc

# Automated Install via Puppet
We have provided a simple manifest file that will install the nose framework via Puppet, 
a configuration management utility. The supplied manifest will automatically detect operating 
system version and install the correct version of nose. Note - We currently support CentOS5, 
CentOS6, and SLES 11 SP2.
