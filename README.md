# SG Project

### Creating Virtual Environment with Requirements (**python3.10**+)
Make python and pip commands run python3 and pip3 and install virtualenv if you don't have it already.
```bash
sudo apt-get update -y &&
sudo apt-get install python3-pip python-is-python3 -y &&
python -m pip install --upgrade pip &&
python -m pip install virtualenv
```

Create a virtual environment named `.venv`

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

### Requirements

Install the requirements.

```bash
pip install -r requirements.txt
```
<!-- pip install --use-deprecated=legacy-resolver -r requirements.txt
# or install without cuda
grep -iv "cuda" requirements.txt | python -m pip install --no-deps -r /dev/stdin  -->

#### Other Requirements
Put the secret key and db info (that is needed to generate token and database access) in `.env` file in root. (Like in `.env.example`)

<!-- ### Models
- Run [this](./app/src/model_downloader.py) code to download the model/s.

Download required model/s and put it in `models` folder.  
For now only NER model is used. -->

### Running the app on terminal
```bash
python app/main.py
```
### Running the app with UI
```bash
python app/serve/api.py
```
