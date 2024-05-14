#!/usr/bin/env python

import subprocess
import time

print('🏀', 'Subprocess.call: run.py')
p = subprocess.Popen(["python", "main.py"])
time.sleep(60)

print('🔫', 'Kill: run.py')
p.kill()
