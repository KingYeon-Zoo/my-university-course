#!/bin/sh
set -eu

socat TCP-LISTEN:9000,fork,reuseaddr TCP:minio:9000 &

exec java -jar exam.jar
