#!/bin/bash
exec celery -A tasks worker --loglevel=info --concurrency=4