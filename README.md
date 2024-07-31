# SweLL-scripts
A collection of scripts for working with the Swedish Learner Language corpora, [SweLL-gold](https://spraakbanken.gu.se/resurser/swell-gold) and [SweLL-pilot](https://spraakbanken.gu.se/resurser/swell-pilot).

## [`dataloaders.py`](dataloaders.py)

SweLL-pilot has individual files for each essay with the following format:

```
essay id: XXXXXX
metadata: XXXXXX

source: XXXXXX [text as transcribed from the original essays]

target: XXXXXX [source text normalised]

svala graph: XXXXXX
```

The dataloaders script has two functions at the moment:

```read_swell_file``` takes as input the path for one of these files and returns a dictionary with an entry for each of the items in the aforementioned format.
For more details on what the keys to the dictionary contain, you can check it's documentation [here](https://github.com/spraakbanken/SweLL-scripts/blob/222a2d2e407dceed8985f9e23acdd49b97ee3b83/dataloaders.py#L85).

```read_swell_directory``` takes as an input the path to the unzipped SweLL folder.
It will return a list with the dictionaries from the ```read_swell_file``` for each essay in the folder.

Note that it has only been tested with SweLL-Pilot as of 2024-04-15.

## [`extract_sentence_pairs.py`](extract_sentence_pairs.py)
A script to extract sentence-correction (also known as original-target) pairs from SweLL-gold XML files.

Alignments are obtained by simply filtering out essays where the original and target do not have the same number of sentences.

To facilitate further processing, anonymization placeholders such as "X-stad" and "X-land-gen" are replaced with naïve pseudonyms such as "Berlin" and "Tysklands" (cf. `placeholder_map`).

Both essay metadata and token-level error labels are retained.
The output can be:
- a TSV file, where error labels are gathered into a single field 
- a CoNNL-U file, where they are stored in each token's MISC field.

### Usage
```
python extract_sentence_pairs.py PATH/TO/sourceSweLL.xml PATH/TO/targetSweLL.xml [--format=tsv|conllu] [--outfile=OUTFILE] 
```

Note that when `--format=conllu`, the program will write two files, named `org-OUTFILE` and `trg-OUTFILE`.

## [`multigec.py`](multigec.py)
Script for converting the SweLL-gold corpus into [the Markdown-based format required for the 2025 MultiGEC shared task](https://github.com/spraakbanken/multigec-2025?tab=readme-ov-file#data-format).
For plain-text text extraction and pseudonymization, it relies on functions defined in [`extract_sentence_pairs`](extract_sentence_pairs.py).
Essays are randomly divided into a train, dev and test set.

### Usage
```
python multigec.py PATH/TO/sourceSweLL.xml PATH/TO/targetSweLL.xml
```

The output is a set of text files following the shared task's naming conventions, which are created in the working directory.   