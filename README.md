# SG Project

### Creating Virtual Environment with Requirements ( _**python3.10**_+ )
Make python and pip commands run python3 and pip3 and install virtualenv if you don't have it already.
```bash
sudo apt-get update -y &&
sudo apt-get install python3-pip python-is-python3 build-essential -y &&
python -m pip install --upgrade pip &&
python -m pip install virtualenv
```

Create a virtual environment named `.venv` and activate it for the current project.

```bash
python -m virtualenv .venv && source .venv/bin/activate
```

### Activation / Deactivation 
Next time the project workstation is opened, these commands can be used to activate the virtual environment.
```bash
# You can activate the virtual environment with the following command.
. .venv/bin/activate

# You can deactivate the virtual environment with the following command.
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
Put the secret key and db access info (that is needed to generate token and database access) in `.env` file in root directory. (Like the example structure in `.env.example` file)

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
