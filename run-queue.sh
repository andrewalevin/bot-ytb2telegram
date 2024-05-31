#!/bin/bash

source venv/bin/activate

# huey_consumer.py taskdownloading.huey -k process -w 4

dramatiq --processes 2 --threads 1  --pid-file pid-dramatiq.pid --log-file log-dramatiq.log taskdownloading
