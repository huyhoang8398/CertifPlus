!#/bin/bash
touch ./ts/ts_respond.tsr
curl -H "Content-Type: application/timestamp-query" --data-binary "@./ts/ts_query.tsq" https://freetsa.org/tsr > ./ts/ts_respond.tsr
