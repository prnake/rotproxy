#!/bin/bash

cp /app/gost.template.yml /app/gost.yml

sed -i "s/USERNAME/${GOST_USERNAME}/g" /app/gost.yml
sed -i "s/PASSWORD/${GOST_PASSWORD}/g" /app/gost.yml

/app/gost -C /app/gost.yml