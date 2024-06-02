#!/bin/bash

./run-queue.sh > log-queue.log 2>&1 &

./run-bot.sh > log-bot.log 2>&1 &

wait