#!/bin/bash
echo Hello

python3 -m flask init-db
#python3 -m flask create-default-users
#python3 -m flask list-users
python -m flask run --host=0.0.0.0

#//CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]