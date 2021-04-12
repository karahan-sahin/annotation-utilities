import re
from conllu import serializer, parse_tree
import conllu
from conllu.models import TokenList, Metadata
import copy
from tkinter import Tk  
from tkinter.filedialog import askopenfilename
import sys

# Copula token line_id and variations
REGEX_LPUNCT = r"\n(\d+)\t(\"[^\t].+?)\t"
REGEX_RPUNCT = r"\n(\d+)\t([^\t]\w+\")(\w*)\t"
REGEX_RDOT = r"\n(\d+)\t(\.+\")(\w*)"

# Total number of capture
# train 506 
# test  39

# Sentence block containing copula
REGEX_BLOCK = '(\# sent_id = {}\n# text = (.+?)\n)((.|\n)+?)\n(?=# sent_id)'

def check_split(item):
    if item["head"] == None:
        return True
    return False

# Updates the iterated token heads
def fix_head(item, cop_id, inc=1):
    try:
        if item["head"] >= cop_id:
            a = item["head"]
            item["head"] += inc
    except:
        pass


file_name = "boun_ud_train_v1.conllu"
data = open(file_name,"r", encoding="utf-8").read()

punct_errors = re.findall(REGEX_LPUNCT,data)

for line,word in punct_errors:

    REGEX_COPBLOCK = f"# sent_id = (\w+_\d+)((?:.*\\n){{{str(int(line))},{str(int(line)+5)}}})(?={line}\\t{word})"
    try:
        ID = re.search(REGEX_COPBLOCK, data).group(1)
    except:
        print("Multi split")
        continue

    if ID == "news_1888":
        continue

    # Whole sentence block
    block = re.search(REGEX_BLOCK.format(ID), data).group(0)
    # Sentence metadata
    metadata = re.search(REGEX_BLOCK.format(ID), data).group(1)

    sentence = conllu.parse(block)[0]

    new_sentence = []

    punct_seen = False
    secondary_punct = True
    line = int(line)
    token_id = line -1

    for i in range(len(sentence)):

        fix_head(sentence[i], int(line))

        if check_split(sentence[i]) and punct_seen:
            sentence[i]["id"] = (sentence[i]["id"][0] + 1,'-',sentence[i]["id"][2] + 1)
            new_sentence.append(sentence[i])
            continue

        if check_split(sentence[i]) and not punct_seen:
            token_id += 1

        if punct_seen:
            hold = sentence[i]
            hold["id"] += 1
            new_sentence.append(hold)

        if i == token_id:
            new_sentence.append({'id': line, # Split token id 
                                'form': '\"', 
                                'lemma': '\"', 
                                'upos': 'PUNCT', 
                                'xpos': "Punc", 
                                'feats': None, 
                                'head': line + 1, 
                                'deprel': 'punct', 
                                'deps': None, 
                                'misc': 'SpaceAfter=No'}) # Add SpaceAfter=No
            
            new_sentence.append({'id': line+1, # Split token id 
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
            continue
        
        if sentence[i]["form"] == "\"" and secondary_punct:
            new_sentence[line-1]["head"] = sentence[i]["head"]
            secondary_punct = False

    
    new_sentence = str(metadata + TokenList(new_sentence).serialize())

    f_out = open(file_name, "w", encoding="utf-8")

    data = re.sub(REGEX_BLOCK.format(ID),new_sentence, data)
    data = re.sub(r'SpacesAfter=\n', r'SpacesAfter=\\n', data)

    f_out.write(data)
    f_out.close()

## Right " 

punct_errors = re.findall(REGEX_RPUNCT,data)

for line, word, suffix in punct_errors:

    REGEX_COPBLOCK = f"# sent_id = (\w+_\d+)((?:.*\\n){{{str(int(line))},{str(int(line)+5)}}})(?={line}\\t{word})"
    try:
        ID = re.search(REGEX_COPBLOCK, data).group(1)
    except:
        print("Multi split")
        continue

    # Whole sentence block
    block = re.search(REGEX_BLOCK.format(ID), data).group(0)
    # Sentence metadata
    metadata = re.search(REGEX_BLOCK.format(ID), data).group(1)

    sentence = conllu.parse(block)[0]

    new_sentence = []

    punct_seen = False
    line = int(line)
    token_id = line-1
    incr = 1
    head = None

    for i in range(len(sentence)):

        fix_head(sentence[i], int(line), incr)

        if check_split(sentence[i]) and punct_seen:
            sentence[i]["id"] = (sentence[i]["id"][0] + incr,'-',sentence[i]["id"][2] + incr)
            new_sentence.append(sentence[i])
            continue

        if check_split(sentence[i]) and not punct_seen:
            token_id += 1

        if punct_seen:
            hold = sentence[i]
            hold["id"] += incr
            new_sentence.append(hold)

        if sentence[i]["form"] == "\"" and not punct_seen:
            head = sentence[i]["head"]

        if i == token_id:
            new_sentence.append({'id': line, # Split token id 
                                'form': word[:-1], 
                                'lemma': word[:-1], 
                                'upos': sentence[i]["upos"], 
                                'xpos': sentence[i]["xpos"], 
                                'feats': sentence[i]["feats"], 
                                'head': sentence[i]["head"], 
                                'deprel': sentence[i]["deprel"], 
                                'deps': None, 
                                'misc': 'SpaceAfter=No'}) # Add SpaceAfter=No

            new_sentence.append({'id': line+1, # Split token id 
                                'form': '\"', 
                                'lemma': '\"', 
                                'upos': 'PUNCT', 
                                'xpos': "Punc", 
                                'feats': None, 
                                'head': head or line, 
                                'deprel': 'punct', 
                                'deps': None, 
                                'misc': None}) # Add SpaceAfter=No
            
            if suffix != '':
                new_sentence.append({'id': line+2, # Split token id 
                                    'form': suffix, 
                                    'lemma': suffix, 
                                    'upos': 'PART', 
                                    'xpos': "Case", 
                                    'feats': None, 
                                    'head': line + 1, 
                                    'deprel': 'punct', 
                                    'deps': None, 
                                    'misc': None}) # Add SpaceAfter=No
                incr += 1
            punct_seen = True

        if not punct_seen:
            new_sentence.append(sentence[i])
            continue
    
    new_sentence = str(metadata + TokenList(new_sentence).serialize())

    f_out = open(file_name, "w", encoding="utf-8")

    data = re.sub(REGEX_BLOCK.format(ID),new_sentence, data)
    data = re.sub(r'SpacesAfter=\n', r'SpacesAfter=\\n', data)

    f_out.write(data)
    f_out.close()




punct_errors = re.findall(REGEX_RDOT,data)

for line, word, suffix in punct_errors:

    word = word.encode("unicode-escape").decode()
    REGEX_COPBLOCK = f"# sent_id = (\w+_\d+)((?:.*\\n){{{str(int(line))},{str(int(line)+5)}}})(?={line}\\t{word})"
    
    try:
        ID = re.search(REGEX_COPBLOCK, data).group(1)
    except:
        print("Multi split")
        continue

    # Whole sentence block
    block = re.search(REGEX_BLOCK.format(ID), data).group(0)
    # Sentence metadata
    metadata = re.search(REGEX_BLOCK.format(ID), data).group(1)

    sentence = conllu.parse(block)[0]

    new_sentence = []

    punct_seen = False
    line = int(line)
    token_id = line-1
    incr = 1
    head = None

    for i in range(len(sentence)):

        fix_head(sentence[i], int(line), incr)

        if check_split(sentence[i]) and punct_seen:
            sentence[i]["id"] = (sentence[i]["id"][0] + incr,'-',sentence[i]["id"][2] + incr)
            new_sentence.append(sentence[i])
            continue

        if check_split(sentence[i]) and not punct_seen:
            token_id += 1

        if punct_seen:
            hold = sentence[i]
            hold["id"] += incr
            new_sentence.append(hold)

        if sentence[i]["form"] == "\"" and not punct_seen:
            head = sentence[i]["head"]

        if i == token_id:
            new_sentence.append({'id': line, # Split token id 
                                'form': word[:-1], 
                                'lemma': word[:-1], 
                                'upos': sentence[i]["upos"], 
                                'xpos': sentence[i]["xpos"], 
                                'feats': sentence[i]["feats"], 
                                'head': sentence[i]["head"], 
                                'deprel': sentence[i]["deprel"], 
                                'deps': None, 
                                'misc': 'SpaceAfter=No'}) # Add SpaceAfter=No

            new_sentence.append({'id': line+1, # Split token id 
                                'form': '\"', 
                                'lemma': '\"', 
                                'upos': 'PUNCT', 
                                'xpos': "Punc", 
                                'feats': None, 
                                'head': head or line, 
                                'deprel': 'punct', 
                                'deps': None, 
                                'misc': None}) # Add SpaceAfter=No
            
            if suffix != '':
                new_sentence.append({'id': line+2, # Split token id 
                                    'form': suffix, 
                                    'lemma': suffix, 
                                    'upos': 'PART', 
                                    'xpos': "Case", 
                                    'feats': None, 
                                    'head': line + 1, 
                                    'deprel': 'punct', 
                                    'deps': None, 
                                    'misc': None}) # Add SpaceAfter=No
                incr += 1
            punct_seen = True

        if not punct_seen:
            new_sentence.append(sentence[i])
            continue
    
    new_sentence = str(metadata + TokenList(new_sentence).serialize())

    f_out = open(file_name, "w", encoding="utf-8")

    data = re.sub(REGEX_BLOCK.format(ID),new_sentence, data)
    data = re.sub(r'SpacesAfter=\n', r'SpacesAfter=\\n', data)

    f_out.write(data)
    f_out.close()


