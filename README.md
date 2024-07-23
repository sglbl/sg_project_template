# MY Project

### Creating Virtual Environment with Requirements
Make python and pip commands run python3 and pip3 and install virtualenv if you don't have it already.
```bash
sudo apt-get update
sudo apt-get install python3-pip python-is-python3
sudo apt-get install build-essential libpython3-dev libdbus-1-dev libglib2.0 libpq-dev python-dev 
python -m pip install virtualenv
```

Create virtual environment.

```bash
python -m virtualenv .venv
```

Activate virtual environment.

```bash
source .venv/bin/activate
```

You can deactivate virtual environment with the following command.

```bash
deactivate
```

### Installation of requirements

Install requirements.

```bash
pip install --use-deprecated=legacy-resolver -r requirements.txt
```

### Models
There are 2 types of models used.
- Run [this](./app/src/model_downloader.py) code to download the models.

Download required model/s and put it in `models` folder.  
For now only NER model is used.

### Other Requirements
Put the secret key and db info (that is needed to generate token and database access) in `.env` file in root. (Like in `.env.example`)

### Running the app on terminal
```bash
python app/main.py
```
### Running the app with UI
```bash
python app/serve/api.py
```
