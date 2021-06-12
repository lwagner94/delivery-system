#!/bin/bash

docker-compose -f docker-compose-test.yml up -d --build

# Wait some time for the services to start up
# ugly, but necessary.
sleep 5

cd integration-test

docker-compose build
docker-compose up

cd ..
docker-compose -f docker-compose-test.yml down