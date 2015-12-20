# poem_generator

Generate Chinese poem automatically.

## Requirements

* Python 3.0+
* Flask
* jieba
* sklearn

## Usage

For the first time, run the commands below to init.

```bash
python preprocess.py
python get_collocations.py
python get_topic.py
python get_start_words.py
```

Next time, just run this command.

```bash
python index.py
```

## Data

In `./data` folder, there is a corpus file "唐诗语料库.txt", and some data files will be generated here.