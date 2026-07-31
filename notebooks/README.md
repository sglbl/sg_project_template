# Notebooks & Marimo Guidance

This directory contains interactive exploration notebooks.

We recommend placing all exploratory notebooks in the root `notebooks/` directory rather than inside `src/` to keep application modules clean and decoupled from interactive scripts.

---

## Using Marimo

[Marimo](https://marimo.io/) is a reactive, pure-Python notebook format stored as standard Python `.py` files.  
Install extension: https://marketplace.visualstudio.com/items?itemName=marimo-team.vscode-marimo


### 1. Edit and Run Marimo as a Web App
Marimo notebooks can also be served directly as interactive web applications:

```bash
# Directly run as web app
marimo run notebooks/explore_marimo.py

# Edit mode that lets you toggle between code and run views with outline option
marimo edit notebooks/explore_marimo.py
```

### 2. Convert / Export Notebooks
Marimo supports bidirectional conversion between `.py` scripts and Jupyter `.ipynb` notebooks:

```bash
# Convert Jupyter notebook to Marimo script
marimo convert notebooks/trial.ipynb -o notebooks/trial_marimo.py

# Export Marimo notebook to static HTML
marimo export html notebooks/explore_marimo.py -o notebooks/explore.html
```

---

## 📁 Directory Structure

```
notebooks/
├── README.md           # Instructions & best practices
├── explore_marimo.py   # Interactive Marimo notebook
└── trial.ipynb         # Jupyter notebook
```
