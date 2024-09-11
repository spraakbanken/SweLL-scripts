### This code can be used to extract pairs of sentences from the SweLL-gold corpus sources (originals) and targets (correction hypotheses) where the two have the same length.

import xml.etree.ElementTree as ET
import argparse
import csv
import conllu
import random

#######################################################################

### This is used to replace "pseudonyms" like A-stad or B-land with something more readable (but not necessarily logically coherent).
placeholder_map = {  # baseline "pseudonymization"
    'kurs': ['kurs'],
    'kursen': ['kursen'],
    'skola': ['Buroskola', 'Andeskola', 'Storeskola', 'Bungahjulet'],
    'region': ['Sydlunda', 'Undered', 'Hanskim', 'Bungalarna'],
    'svensk-stad': ['Sydden', 'Norrebock', 'Rosaborg', 'Ögglestad'],
    'institution': ['Volvodrömen', 'Linsbiblioteket', 'Forkecentralen', 'Bungavård'],
    'geoplats': ['Fafjällen', 'Undberget', 'Baraön', 'Lokomitt'],
    'linjen': ['buss'],
    'stad-gen': ['Syddens', 'Norrebocks', 'Rosaborgs', 'Ögglestads'],
    'stad': ['Oslo', 'Paris', 'Bagdad', 'Caracas'],
    'land': ['Danmark', 'Mongoliet', 'Sudan', 'Peru'],
    'land-gen': ['Danmarks', 'Mongoliets', 'Sudans', 'Perus'],
    'hemland': ['Brasil', 'Spanien', 'Irak', 'Kina'],
    'plats': ['Burocentrum', 'Andeplats', 'Storetorg', 'Bungafors']
    }
    
#######################################################################

def get_essays(file: str):
    '''A function that retrieves the data from a SweLL xml file and splits it into essays.
    
    Args:
        file (str): Path and name of the file.
        
    Returns:
        A list of essays.
    '''
    tree = ET.parse(file)
    root = tree.getroot()
    
    essays = []
    essay = []
    for elem in root.iter():
        if elem.tag == 'text':
            if len(essay) > 1:  # exclude meaningless
                essays.append(essay)
            essay = []
        essay.append((elem.tag, elem.text, elem.attrib))
    essays.append(essay)

    return essays

def get_sent_dict(essays: list, replace_nls: bool=False):
    '''A function that retrieves sentences for every essay.
    
    Args:
        essays (list): A list of essays retrieved from the XML file.
        replace_nls (bool): A flag specifying whether ␤ characters are to be replaced with \n. If set to False, ␤s do NOT appear in the final output
        
    Returns:
        A list of essays.
    '''
    essay_dict = {}
    essay_sents = []
    for essay in essays:
        metadata = essay[0][2] 
        essay_id = metadata['essay_id']
        sent = []
        for (cat,word,info) in essay[1:]:  # without metadata
            if replace_nls: 
                word = word.replace("␤", "\n")
            if cat == 'link':
                continue
            elif cat == 'sentence':
                if len(sent) > 0:
                    essay_sents.append(sent)
                    sent = []
            else: 
                if '␤' not in word and essay_id not in word:
                    if 'A-' in word or 'B-' in word or 'C-' in word or 'D-' in word:
                        try:
                            word = random.choice(placeholder_map[word[2:]])
                        except KeyError:
                            pass
                    sent.append((word, info["correction_label"] if "correction_label" in info else "_"))
    
        essay_sents.append(sent)
        essay_dict[essay_id] = {"metadata": metadata, "sentences": essay_sents}
        essay_sents = []
        
        
    return essay_dict 

def pair_up(source_dict: dict, target_dict: dict):
    '''A function that selects the essays with equal number of sentences in both source and target and aligns them naively.
    
    Args:
        source_dict (dict): A dictionary with source sentences.
        target_dict (dict): A dictionary with target sentences.
        
    Returns:
        A list tuples of (original sentence, target sentence, essay ID).
    '''
    paired_up = []
    for essay_id, val in source_dict.items():
        metadata = val["metadata"]
        assert metadata == target_dict[essay_id]["metadata"]
        sentences = val["sentences"]
        if len(sentences) == len(target_dict[essay_id]["sentences"]):
            for i, sent in enumerate(sentences):
                paired_up.append({
                    "original": sent, 
                    "target": target_dict[essay_id]["sentences"][i], 
                    "metadata": metadata})
    return paired_up

def tokenlist(word_label_pairs, metadata):
    '''
    Build a conllu.TokenList out of the sentence-level information extracted 
    from SweLL.

    Args:
        word_label_pairs (list): a list of word-correction label pairs.
        metadata (dict): metadata of the essay the sentence belongs to, directly in SweLL format.

    Returns:
        a conllu.TokenList representing the sentence.
    '''
    tokens = []
    for i, (word,label) in enumerate(word_label_pairs):
        tokens.append(conllu.Token(
            id=i + 1, 
            form=word, 
            lemma="_",
            upos="_",
            xpos="_",
            feats="_",
            head="_",
            deprel="_",
            deps="_",
            misc=label))
    return conllu.TokenList(tokens=tokens, metadata=metadata)

if __name__ == "__main__":
    formats = ["tsv", "conllu"]
    parser = argparse.ArgumentParser()

    parser.add_argument('source', help='The path to the sourceSweLL.xml file')
    parser.add_argument('target', help='The path to the targetSweLL.xml file')
    parser.add_argument('--format', required=False, default="tsv", help='output format (tab-separated or CONLL-U)', type=str, choices=formats)
    parser.add_argument('--outfile', required=False, default="swell_sent_pairs.tsv", type=str, help='The name for the output file. If outputting CoNLL-U "org-" resp. "trg-" are added to the corresponding filenames')
    
    args = parser.parse_args()
     
    source_essays = get_essays(args.source)
    target_essays = get_essays(args.target)
    output_format = args.format
    if not output_format in formats:
        print("invalid format, please select 'conllu' or 'tsv'")
        exit(-1)
    
    source_dict = get_sent_dict(source_essays)
    target_dict = get_sent_dict(target_essays)

    pairs = pair_up(source_dict, target_dict)
    
    if output_format == "tsv":
        with open(args.outfile, "w") as outfile:
            for (i,pair) in enumerate(pairs):
                
                org_sent = " ".join([token for (token,_) in pair["original"]])
                trg_sent = " ".join([token for (token,_) in pair["target"]])
                labels = ",".join([label for (_,label) in pair["original"] if label != "_"])
                csv_row = pair["metadata"] | {"original sentence": org_sent, "corrected sentence": trg_sent, "correction labels": labels}
                writer = csv.DictWriter(outfile, csv_row.keys(), delimiter="\t")
                if i == 0: writer.writeheader()
                writer.writerow(csv_row)     

    else: # conllu
        with open("org-" + args.outfile, "w") as org_outfile, open("trg-" + args.outfile, "w") as trg_outfile:
            for pair in pairs:
                metadata = pair["metadata"]
                org_sent = tokenlist(pair["original"], metadata)
                trg_sent = tokenlist(pair["target"], metadata)
                org_outfile.write(org_sent.serialize())
                trg_outfile.write(trg_sent.serialize())
            
