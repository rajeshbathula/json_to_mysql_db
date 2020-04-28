FROM mysql:latest

# The official MySQL docker image will run all .sh and .sql scripts found in this directory
# the first time the container is started.
COPY init.sql /docker-entrypoint-initdb.d
