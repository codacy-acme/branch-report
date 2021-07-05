# branch-report

A tool to list all repositories on an organization, the metrics on the main branch of each repo and if certain repos (via param) are enabled


## Usage

Create a file named auth.cookie and dump inside it the value of your Codacy cookie.

The `requirements.txt` lists all Python libraries that should be installed before running the script:

```bash
pip install -r requirements.txt
```

### Command

```bash
python3 main.py  --token {token} --provider {provider} --organization {organization}
```

### Generate CSV

```bash
python3 main.py  --token {token} --provider {provider} --organization {organization} --output output.csv
```