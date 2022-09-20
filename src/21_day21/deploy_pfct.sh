#!/usr/bin/bash
prefect work-queue create day21 -l 1
prefect deployment build pfct.py:pull_to_trigger -n pull_to_trigger -t pull_to_trigger -q day21
prefect deployment apply pull_to_trigger-deployment.yaml
prefect agent start -q 'day21'

