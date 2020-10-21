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
