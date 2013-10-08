#!/bin/sh

mv planner/fixtures/initial_data.json planner/fixtures/initial_data_old.json
python manage.py dumpdata --indent=4 planner > planner/fixtures/initial_data.json

