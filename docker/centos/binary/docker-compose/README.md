Docker Compose (ie Fig)
=======================

[![wercker status](https://app.wercker.com/status/d5dbac3907301c3d5ce735e2d5e95a5b/s/master "wercker status")](https://app.wercker.com/project/bykey/d5dbac3907301c3d5ce735e2d5e95a5b)

Fast, isolated development environments using Docker.

Define your app's environment with Docker so it can be reproduced anywhere:

    FROM python:2.7
    COPY . /code
    WORKDIR /code
    RUN pip install -r requirements.txt
    CMD python app.py

Define the services that make up your app so they can be run together in an isolated environment:

```yaml
web:
  build: .
  links:
   - db
  ports:
   - "8000:8000"
   - "49100:22"
db:
  image: postgres
```

(No more installing Postgres on your laptop!)

Then type `docker-compose up`, and Compose will start and run your entire app.

There are commands to:

 - start, stop and rebuild services
 - view the status of running services
 - tail running services' log output
 - run a one-off command on a service

Installation and documentation
------------------------------

Full documentation is available on [Docker's website](https://docs.docker.com/compose/).

Use wtih Kolla
--------------

Docker-compose is being used to compose one or more co-located containers know
as [container sets][]. docker-compose is deployed as a container from the
kollaglue [repository][] to Kolla nodes using the Heat orchestration
[template]. The docker-compose container creates a host mount to communicate
with the docker api over a unix socket. The docker engine could be configured
to expose the API over TCP and may be evaluated for future use. An additional
host mount to /opt/docker-compose for docker-compose to read the .yml file.
This allows for seperating the docker-compose code from the data/configuration
information.

Either create or modify the existing docker-compose.yml file at
/opt/docker-compose. Here is a simple example of a single container for
RabbitMQ:

```
rabbitmq:
  image: kollaglue/fedora-rdo-rabbitmq
  environment:
    RABBITMQ_NODENAME: rabbit01
    RABBITMQ_USER: rabbit
    RABBITMQ_PASS: password
  net: "host"
  ports:
    - "5672:5672"
    - "15672:15672"
    - "4369:4369"
    - "25672:25672"
  privileged: true
```

Then run up to instantiate the container-set:
```
$ docker run --privileged -v /opt/docker-compose:/opt/docker-compose -v /var/run/docker.sock:/var/run/docker.sock kollaglue/fedora-rdo-docker-compose up -d
```
The -d flag tells docker-compose to run the container set in daemonized mode.

[container sets]: https://github.com/stackforge/kolla/blob/master/specs/containerize-openstack.rst
[template]: https://github.com/stackforge/kolla/tree/master/devenv
[repository]: https://registry.hub.docker.com/u/kollaglue/fedora-rdo-docker-compose/

Contribute to Kolla Fig
-----------------------

Clone the repo:
```
git clone https://github.com/docker/compose.git
```
Set the following ENVs in the project's Dockerfile:
```
ENV COMPOSE_PROJECT_NAME kollaglue-fedora-rdo
ENV COMPOSE_FILE /opt/docker-compose/docker-compose.yml
```
Hack as needed, then build the image:
```
$ docker build -t kollaglue/kollaglue-fedora-rdo-docker-compose .
```
Push the image to the kollaglue repo
```
$ docker push kollaglue/fedora-rdo-docker-compose:latest
```
