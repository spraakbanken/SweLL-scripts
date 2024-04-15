import xml.etree.ElementTree as ET
import pandas as pd
import os
import argparse

#######################################################################

placeholder_map = {  # baseline "pseudonymization"
    'kurs': 'kurs',
    'kursen': 'kursen',
    'skola': 'Umeå universitet',
    'region': 'Skåne',
    'svensk-stad': 'Stockholm',
    'institution': 'Domkyrkan',
    'geoplats': 'Östersjön',
    'linjen': 'Öresundståg',
    'stad-gen': 'Stockholms',
    'stad': 'Berlin',
    'land': 'Tyskland',
    'land-gen': 'Tysklands',
    'hemland': 'Polen',
    'plats': 'Renströmsgatan'
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

def get_sent_dict(essays: list):
    '''A function that retrieves sentences for every essay.
    
    Args:
        essays (list): A list of essays retrieved from the XML file.
        
    Returns:
        A list of essays.
    '''
    essay_dict = {}
    essay_sents = []
    for essay in essays:
        essay_id = essay[0][2]['essay_id']
        sent = []
        sent_err_labels = []
        for elem in essay[1:]:  # without metadata
            if elem[0] == 'link':
                continue
            elif elem[0] == 'sentence':
                if len(sent) > 0:
                    essay_sents.append((sent, sent_err_labels))
                    sent = []
                    sent_err_labels = []
            else:
                sent.append(elem[1])
                if "correction_label" in elem[2]:
                    sent_err_labels.append(elem[2]["correction_label"])
    
        essay_sents.append((sent, sent_err_labels))
        essay_dict[essay_id] = essay_sents
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
    for k, v in source_dict.items():
        if len(v) == len(target_dict[k]):
            for i, (sent, labels) in enumerate(v):
                paired_up.append((sent, target_dict[k][i][0], k, labels))
    return paired_up

def replace_placeholders(sentence: list, placeholder_map: dict, essay_id: str):
    '''A function that replaces anonymized tokens with some mapping, and removes the essay ID and newline from the essay.
    
    Args:
        sentence (list): A sentence represented as a list of tokens.
        placeholder_map (dict): A dictionary mapping possible placeholders to other tokens.
        essay_id (str): The ID of the essay the sentence is from.
        
    Returns:
        A list tuples of (original sentence, target sentence, essay ID).
    '''
    for i, word in enumerate(sentence):
        if 'A-' in word or 'B-' in word or 'C-' in word or 'D-' in word:
            try:
                sentence[i] = placeholder_map[word[2:]]
            except KeyError:
                continue
        sentence = [word for word in sentence if '␤' not in word and essay_id not in word]
    return sentence

def create_df(paired_up, placeholder_map):
    '''A function that creates a DataFrame out of the paired up sentences and replaces the placeholder tokens with naive surrogates.
    
    Args:
        paired_up (list): A list of paired-up sentences.
        placeholder_map (dict): A dictionary mapping possible placeholders to other tokens.
        
    Returns:
        A pandas DataFrame with the original sentence, target sentence, and essay ID with undesirable elements removed.
    '''
    sentence_pairs = []
    for pair in paired_up:
        essay_id = pair[2]
        labels = pair[3]
        sent1 = ' '.join(replace_placeholders(pair[0], placeholder_map, essay_id))
        sent2 = ' '.join(replace_placeholders(pair[1], placeholder_map, essay_id))
        
        sentence_pairs.append((sent1, sent2, essay_id, ",".join(labels)))

    df = pd.DataFrame(sentence_pairs)
    df.columns = ['Source sentence', 'Target sentence', 'Essay ID', 'Correction labels']
    df.set_index("Source sentence", inplace=True)
    return df
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('source', help='The path to the sourceSweLL.xml file')
    parser.add_argument('target', help='The path to the targetSweLL.xml file')
    parser.add_argument('--filename', required=False, default='aligned_sentences.tsv', help='The name for the output file.')
    
    args = parser.parse_args()
     
    source_essays = get_essays(args.source)
    target_essays = get_essays(args.target)
    
    source_dict = get_sent_dict(source_essays)
    target_dict = get_sent_dict(target_essays)

    paired_up = pair_up(source_dict, target_dict)
    
    df = create_df(paired_up, placeholder_map)
    
    # save as a TSV file
    df.to_csv(args.filename, sep='\t')
    