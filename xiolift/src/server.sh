
#!/bin/bash

dir='xiolift/src'

nohup streamlit run ${dir}/MyWeb.py --server.port 5000 > /dev/null 2>&1 &

nohup python ${dir}/MyFastApi.py > /dev/null 2>&1 &
