# e-mission-transfer
This repository contains scripts to import/export data from e-mission
instances. Since there are multiple deployment scenarios, there is not likely
to be one set of scripts that works for everybody.

So we can add scripts for various scenarios here as needed. If we do converge
on a single deployment mechanism, we can delete this repository 🙂

Scenario 1:
  - Apache reverse proxy, also running basic website
  - e-mission running in docker containers
  - extract from docker
  - encrypt on server
  - publish on basic website

Scenario 2:
  - Apache reverse proxy, also running basic website
  - e-mission running in docker containers
  - mongodump from docker
  - encrypt on server
  - publish on basic website

Scenario 3:
  - multiple instances of e-mission running on the same physical server
  - multiple docker containers
  - container can be inferred from user email
  - extract in docker
  - copy to server
  - ssh access to the server
  - don't publish; will retrieve via scp
