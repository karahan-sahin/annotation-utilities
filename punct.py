import re
from conllu import serializer, parse_tree
import conllu
from conllu.models import TokenList, Metadata
import copy
from tkinter import Tk  
from tkinter.filedialog import askopenfilename
import sys


# Copula token line_id and variations
REGEX_PUNCT = r"\n(\d+)\t(\"[^\t].+?)\t"
# Sentence block containing copula
REGEX_BLOCK = '(\# sent_id = {}\n# text = (.+?)\n)((.|\n)+?)\n(?=# sent_id)'

data = open("boun_ud_test_v1.conllu","r", encoding="utf-8").read()

# Tasks
# 

def check_split(item):
    if item["head"] == None:
        return True
    return False

# Updates the iterated token heads
def fix_head(item, cop_id):
    try:
        if item["head"] > cop_id:
            a = item["head"]
            item["head"] += 1
    except:
        pass

punct_errors = re.findall(REGEX_PUNCT,data)

for line,word in punct_errors:

    REGEX_COPBLOCK = f"# sent_id = (\w+_\d+)((?:.*\\n){{{str(int(line))},{str(int(line)+5)}}})(?={line}\\t{word})"

    try:
        ID = re.search(REGEX_COPBLOCK, data).group(1)
    except:
        print("Multi cop")
        continue

    # Whole sentence block
    block = re.search(REGEX_BLOCK.format(ID), data).group(0)
    # Sentence metadata
    metadata = re.search(REGEX_BLOCK.format(ID), data).group(1)

    sentence = conllu.parse(block)[0]

    new_sentence = []

    punct_seen = False

    for i in range(len(sentence)):
        
        # Fixes iterated heads
        fix_head(sentence[i], int(line))

        if check_split(sentence[i]):
            sentence[i]["id"] = (sentence[i]["id"][0] + 1,'-',sentence[i]["id"][2] + 1)
            new_sentence.append(sentence[i])
            continue

        if punct_seen:
            hold = sentence[i]
            hold["id"] += 1
            new_sentence.append(hold)

        if i == int(line)-1:
            new_sentence.append({'id': int(line), # Split token id 
                                'form': '\"', 
                                'lemma': '\"', 
                                'upos': 'PUNCT', 
                                'xpos': "Punc", 
                                'feats': None, 
                                'head': int(line) + 1, 
                                'deprel': 'punct', 
                                'deps': None, 
                                'misc': 'SpaceAfter=No'}) # Add SpaceAfter=No
            
            new_sentence.append({'id': int(line)+1, # Split token id 
                                'form': word[1:], 
                                'lemma': word[1:], 
                                'upos': sentence[i]["upos"], 
                                'xpos': sentence[i]["xpos"], 
                                'feats': sentence[i]["feats"], 
                                'head': sentence[i]["head"], 
                                'deprel': sentence[i]["deprel"], 
                                'deps': None, 
                                'misc': sentence[i]["misc"]}) # Add SpaceAfter=No
            punct_seen = True

        if not punct_seen:
            new_sentence.append(sentence[i])

    
    new_sentence = str(metadata + TokenList(new_sentence).serialize())

    print

    f_out = open(file_name, "w", encoding="utf-8")

    data = re.sub(REGEX_BLOCK.format(ID),new_sentence, data)
    data = re.sub(r'SpacesAfter=\n', r'SpacesAfter=\\n', data)

    f_out.write(data)
    f_out.close()

