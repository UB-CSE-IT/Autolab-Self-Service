## Create a revision

* Ensure your PYTHONPATH contains the project directory
    * Example on Linux: `export PYTHONPATH=$PYTHONPATH:~/programming/autolab/Autolab-Self-Service`
    * Example on Windows: `set PYTHONPATH=%PYTHONPATH%;C:\Local\Programming\autolab\Autolab-Self-Service`
* Run: `alembic revision --autogenerate -m "message"` in the `backend` directory.
* Review the generated revision file and make any necessary changes. Alembic isn't perfect!
* Add the revision file to version control

## Apply revisions

* Run `alembic upgrade head`
    * This automatically runs in the backend Docker container on startup
    * If it freezes, ensure the application isn't running

## Add a new model

* Import the model in `backend/alembic/env.py`
* Create a revision