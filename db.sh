#!/bin/bash
#--hostname=roach-single   --net=roachnet 
docker run -it  --env COCKROACH_DATABASE=nos_algemeen --env COCKROACH_USER=frank \
 --env COCKROACH_PASSWORD=frank  -p 26257:26257   -p 8080:8080 \
 -v "roach-single:/cockroach/cockroach-data" cockroachdb/cockroach start-single-node --insecure --http-addr=0.0.0.0:8080