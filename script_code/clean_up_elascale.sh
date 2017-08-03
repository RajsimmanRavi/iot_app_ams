#!/bin/bash

sudo docker stack rm EK_monitor

sudo docker stack rm beats

sudo docker service rm ui
