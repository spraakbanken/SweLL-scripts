import argparse
from random import shuffle
from extract_sentence_pairs import get_essays, get_sent_dict

def get_full_text(essay_id, sent_dict):
    return " ".join(
        [" ".join([tok for (tok,_) in sent])
         for sent in sent_dict[essay_id]["sentences"]])

def adjust_whitespace(text):
    text = text.replace("\n ", "\n") # adjust newlines
    # adjust basic punctuation
    for punct_mark in [".", ":", ",", ";", "!", "?"]:
        text = text.replace(" " + punct_mark, punct_mark)
    # adjust parentheses and quotes
    for punct_mark in ["(", "[", "{"]:
        text = text.replace(punct_mark + " ", punct_mark)
    for punct_mark in [")", "]", "}"]:
        text = text.replace(" " + punct_mark, punct_mark)
    return text

def outformat(essay_ids, which, essay_dict): # which = "src"|"trg"
    return "".join(["### essay_id = {}\n{}\n\n".format(
        essay_id, adjust_whitespace(essay_dict[essay_id][which])) 
             for essay_id in essay_ids])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('src', help='The path to the sourceSweLL.xml file')
    parser.add_argument('trg', help='The path to the targetSweLL.xml file')
    
    args = parser.parse_args()

    src_sent_dict = get_sent_dict(get_essays(args.src), replace_nls=True)
    trg_sent_dict = get_sent_dict(get_essays(args.trg), replace_nls=True)

    essay_dict = {
        essay_id: {
            "src": get_full_text(essay_id, src_sent_dict),
            "trg": get_full_text(essay_id, trg_sent_dict)} 
            for essay_id in src_sent_dict }
    
    essay_ids = list(essay_dict.keys())
    shuffle(essay_ids) # just in case essays are in some particular ordered
    with open("sv-swell_gold-orig-dev.md", "w") as dev_orig, open("sv-swell_gold-ref1-dev.md", "w") as dev_ref1:
        dev_orig.write(outformat(essay_ids[:50], "src", essay_dict))
        dev_ref1.write(outformat(essay_ids[:50], "trg", essay_dict))
    with open("sv-swell_gold-orig-test.md", "w") as test_orig, open("sv-swell_gold-ref1-test.md", "w") as test_ref1:
        test_orig.write(outformat(essay_ids[50:100], "src", essay_dict))
        test_ref1.write(outformat(essay_ids[50:100], "trg", essay_dict))
    with open("sv-swell_gold-orig-train.md", "w") as train_orig, open("sv-swell_gold-ref1-train.md", "w") as train_ref1:
        train_orig.write(outformat(essay_ids[100:], "src", essay_dict))
        train_ref1.write(outformat(essay_ids[100:], "trg", essay_dict))
    





