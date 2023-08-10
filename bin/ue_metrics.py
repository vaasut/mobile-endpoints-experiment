#!/usr/bin/env python3
import time

import quectel_control

ue_client = quectel_control.QuectelControlClient()
while True:
    print(ue_client.servingcell())
    time.sleep(1)
