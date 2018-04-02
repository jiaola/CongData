# Congressional Data

## Data

/data

Original data are stored in /data directory. data/bills has all the bills text. data/status has all the status data about the bills, including the sponsors of the bills. 

## Corpus

Tabular data extracted from data dirctory. s-11*.txt are senate bills. hr-11*.txt are house bills. 

## Models

/models

## Scripts

/scripts

## Workflow

* Extract text from bills

```
python scripts/extract_text.py [session]
```
For example: `python scripts/extract_text.py s-113`

Output: `corpus/s-113.txt`

* Process with spacy 

```
python scripts/process_with_spacy.py [session]
```

For example `python process_with_spacy.py s-113`

Output: `corpus/s-113-processed.txt`

* Build model

```
python scripts/build_model.py [session]
```

For example, `python scripts/build_model.py s-113`
