# UPM (Universal Package Manager) (unstable)
UPM is a software package manager inspired from node's npm and apt-get, powered by docker. which is a workspace that wrap your project like package.
and let developer describe their dependency and relations incrementally in their workspace independent of their development os and environment.
every service, library, bin and network will describe once and available in their development workspace and ready for deployment with little to no effort.

## Getting Started
install python package with:
```
pip install upmcli
```
initialize new package:
```
upm init
```
install package:
```
upm install
```
install other package as dependency:(this is going change and replace with upm directory)
```
upm install <pkg_location>
```

### Prerequisites

upm need docker CE and docker-compose to be installed:

for docker installation see [docker documents](https://docs.docker.com/install/#docker-ce)

for docker-compose :
```
pip install docker-compose
```