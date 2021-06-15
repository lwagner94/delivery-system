# Delivery System
## Students
  - Meinhard Kissich (11771817)
  - Klaus Weinberg (11721179)
  - Lukas Wagner (0140206)


## Services

The whole system is split into 4 services:
  - authentication service `src/auth`
  - agent service `src/AgentAPI`
  - job service `src/job`
  - geo service `src/GeoAPI`

In each subdirectory, a `Dockerfile` can be found, which is used to
deploy each service in a container.

## Running the services

To run the services, the following steps must be performed:

```bash
cd src
docker-compose build
docker-compose up
```

After these steps, the service will be available at `http://localhost:8000`.


## Running the integration tests
### Automatic, docker-based test execution
To make sure that the service is fully operational and is compliant to the
specification, a comprehensive test suite was created. 

To run it, first make sure that all services have been stopped. Then execute:
```bash
cd src
./run_tests.sh
```

For Windows:
```bash
.\run_tests.ps1
```

This spins up builds and spins up all services in a special configuration, builds the test driver container, executes the tests
and finally, all containers are stopped again.

### Manual test execution
Alternatively, it is also possible to run the tests in a more manual fashion, which might be helpful when writing new tests, because 
this approach is quite a bit more agile.

First, we need to start our services.
```bash
cd src
docker-compose -f docker-compose-test.yml up --build
```

Then, in a second terminal window, make sure that all necessary python packages are installed. We advise this to be run in a clean python virtual environment. 
```bash
cd src/integration-test
pip3 install -r requirements.txt
```

After that, the integration tests can be run using the following command:
```bash
pytest
```

## Demo App
For demonstration purposes, a simple python application was developed. It is based on the PyQt framework.

To run it, all necessary python packages must be installed first:
```bash
cd src/demo
pip3 install -r requirements.txt
```

Then, the app can be run with the following command:
```bash
python3 demo.py
```

## Pitfalls
 - Originally, the authentication service was written in Rust. It was completely functional, however there were some issues with CORS and due to library versioning issues, this could not be easily solved. For that reason, the service was completely rewritten in Python/Flask
