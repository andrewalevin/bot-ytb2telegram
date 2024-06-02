#!/bin/bash

source venv/bin/activate

# huey_consumer.py taskdownloading.huey -k process -w 4

# Demo Mode
dramatiq --processes 2 --threads 1 taskdownloading


# dramatiq --processes 2 --threads 1  --pid-file pid-dramatiq.pid --log-file log-dramatiq.log taskdownloading
