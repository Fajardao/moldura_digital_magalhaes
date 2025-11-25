#!/bin/bash

while true; do
    if (ps aux | grep "python3 run.py" | grep -v grep) > /dev/null; then
        echo "O serviço já está em execução."
    else
        echo "A iniciar o serviço..."
        python3 run.py &
    fi
    sleep 300
done