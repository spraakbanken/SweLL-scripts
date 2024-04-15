# SweLL-scripts
A collection of scripts for working with the [Swedish Learner Language corpus](https://spraakbanken.gu.se/resurser/swell-gold).

## Contributing
If you have any SweLL-related scripts, you are welcome to add your code and add a few lines to this README saying:

- what the name of your script is
- what it does
- how to run it


## Dataloaders

Swell has individual files for each essay with the following format:

```
essay id: XXXXXX
metadata: XXXXXX

source: XXXXXX [text as transcribed from the original essays]

target: XXXXXX [source text normalised]

svala graph: XXXXXX
```

The dataloaders folder has two functions at the moment:

```read_swell_file``` takes as input the path for one of these files and returns a dictionary with an entry for each of the items in the aforementioned format.
For more details on what the keys to the dictionary contain, you can check it's documentation [here](https://github.com/spraakbanken/SweLL-scripts/blob/222a2d2e407dceed8985f9e23acdd49b97ee3b83/dataloaders.py#L85).

```read_swell_directory``` takes as an input the path to the unzipped Swell folder.
It will return a list with the dictionaries from the ```read_swell_file``` for each essay in the folder.
Note that it has only been tested with Swell-Pilot as of 2024-04-15.
