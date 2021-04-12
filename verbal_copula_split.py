import re
from conllu import serializer, parse_tree
import conllu
from conllu.models import TokenList, Metadata
import sys
import copy
from tkinter import Tk  
from tkinter.filedialog import askopenfilename


# Copula token line_id and variations
REGEX_COP = "\n(\d+)\\t({}(\w*)))\\t"
# Sentence block containing copula
REGEX_BLOCK = '(\# sent_id = {}\n# text = (.+?)\n)((.|\n)+?)\n(?=# sent_id)'

forms = {
    # mış with copulas
    "V+m[iıuü]ş+cop": {
        "V+m[iıuü]ş+t[iıuü]": ["Aspect=Perf|Polarity=Pos|VerbForm=Part", 
                               "Evident=Fh|Number={}|Person={}|Polarity=Pos|Tense=Past"],

        "V+m[iıuü]ş+s[ea]": ["Aspect=Perf|Polarity=Pos|Tense=Past|VerbForm=Part", 
                             "Mood=Cnd|Number={}|Person={}|Polarity=Pos"],

        "V+m[iıuü]ş+m[iıuü]ş": ["Aspect=Perf|Polarity=Pos|VerbForm=Part", 
                                "Evident=Nfh|Number={}|Person={}|Polarity=Pos|Tense=Past"],

        "V+m[iıuü]ş+ken": ["Aspect=Perf|Polarity=Pos|Tense=Past|VerbForm=Part",
                           "Polarity=Pos|VerbForm=Conv"]
    },


    # ıyor with copulas
    "V+[iıuü]yor+cop": {
        "V+[iıuü]yor+d[iıuü]": ["Aspect=Prog|Polarity=Pos|VerbForm=Part", 
                                "Evident=Fh|Number={}|Person={}|Polarity=Pos|Tense=Past"],

        "V+[iıuü]yor+sa": ["Aspect=Prog|Polarity=Pos|Tense=Pres|VerbForm=Part",
                           "Mood=Cnd|Number={}|Person={}|Polarity=Pos"],

        "V+[iıuü]yor+muş": ["Aspect=Prog|Polarity=Pos|VerbForm=Part",
                              "Evident=Nfh|Number={}|Person={}|Polarity=Pos|Tense=Past"],

        "V+[iıuü]yor+ken": ["Aspect=Prog|Polarity=Pos|Tense=Past|VerbForm=Part",
                            "Polarity=Pos|VerbForm=Conv"]
    },

    # dı with copulas
    "V+[td][iıuü]+cop": {
        "V+[td][iıuü]+yd[iıuü]": ["Aspect=Perf|Polarity=Pos|VerbForm=Part",
                                  "Evident=Fh|Number={}|Person={}|Polarity=Pos|Tense=Past"],

        "V+[td][iıuü]+ys[ea]": ["Aspect=Perf|Polarity=Pos|Tense=Past|VerbForm=Part", 
                                "Mood=Cnd|Number={}|Person={}|Polarity=Pos"],

        "V+s[ea]+yd[iıuü]": ["Mood=Cnd|Polarity=Pos",
                             "Aspect=Perf|Evident=Fh|Number={}|Person={}|Polarity=Pos|Tense=Past"]
    }, 

    # [A/I]r with copulas
    "V+[a,ı;u;e,i;ü]r+cop": {
        "V+[a,ı;u;e,i;ü]r+d[ı;u;i;ü]": ["Aspect=Hab|Polarity=Pos|VerbForm=Part",
                                        "Evident=Fh|Number={}|Person={}|Polarity=Pos|Tense=Past"],

        "V+[a,ı;u;e,i;ü]r+s[ea]": ["Aspect=Hab|Polarity=Pos|Tense=Pres|VerbForm=Part",
                                   "Mood=Cnd|Number={}|Person={}|Polarity=Pos"],

        "V+[a,ı;u;e,i;ü]r+m[iıuü]ş": ["Aspect=Hab|Polarity=Pos|VerbForm=Part",
                                      "Evident=Fh|Number={}|Person={}|Polarity=Pos|Tense=Past"],

        "V+[a,ı;u;e,i;ü]r+ken": ["Aspect=Hab|Polarity=Pos|Tense=Pres|VerbForm=Part",
                                 "Polarity=Pos|VerbForm=Conv"]
    },

    # mAz with copulas
    "V+m[ae]z+cop": {
        "V+m[ae]z+d[ıi]": ["Aspect=Hab|Polarity=Neg|VerbForm=Part",
                           "Evident=Fh|Number={}|Person={}|Polarity=Pos|Tense=Past"],

        "V+m[ae]z+s[ae]": ["Aspect=Hab|Polarity=Neg|Tense=Pres|VerbForm=Part",
                           "Mood=Cnd|Number={}|Person={}|Polarity=Pos"],

        "V+m[ae]z+m[ıi]ş": ["Aspect=Hab|Polarity=Neg|VerbForm=Part", 
                            "Evident=Fh|Number={}|Person={}|Polarity=Pos|Tense=Past"],

        "V+m[ae]z+ken": ["Aspect=Hab|Polarity=Neg|Tense=Pres|VerbForm=Part",
                         "Polarity=Pos|VerbForm=Conv"]
    },

    #+[y]AcAk with copulas
    "V+y*[ae]c[ae]k+cop": {
        "V+[y]?+[ae]c[ae]k+t[ı;u;i;ü]": ["Aspect=Prosp|Polarity=Pos|VerbForm=Part",
                                       "Evident=Fh|Number={}|Person={}|Polarity=Pos|Tense=Past"],

        "V+[y]?+[ae]c[ae]k+s[ae]": ["Aspect=Prosp|Polarity=Pos|Tense=Fut|VerbForm=Part",
                                  "Mood=Cnd|Number={}|Person={}|Polarity=Pos"],

        "V+[y]?+[ae]c[ae]k+m[ıu]ş": ["Aspect=Prosp|Polarity=Pos|VerbForm=Part",
                                   "Evident=Fh|Number={}|Person={}|Polarity=Pos|Tense=Past"],

        "V+[y]?+[ae]c[ae]k+ken": ["Aspect=Prosp|Polarity=Pos|Tense=Fut|VerbForm=Part",
                                "Polarity=Pos|VerbForm=Conv"]
    },
}

# Personal Agreement on Predicate
person = {"[ıiuü]?m": ("Sing", 1), 
          "[s]?[ı]?n": ("Sing",2),
          "": ("Sing",3),
          "([^n][ıuüi]?z|k)": ("Plur",1),
          "([s]?[ıuüi]?n[ıuüi]z)": ("Plur",2),
          "(ler)": ("Plur",3),
          }

# If there is a pre-splitted items
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

# Split and update the sentence
def copula_split(sentence, new_sentence, token_index):
    new_sentence.append({'id': (token_id, "-", token_id+1), # Split token id 
                         'form': word, 
                         'lemma': '_', 
                         'upos': '_', 
                         'xpos': None, 
                         'feats': None, 
                         'head': None, 
                         'deprel': '_', 
                         'deps': None, 
                         'misc': '_'}) # Add SpaceAfter=No

    if sentence[token_index]["misc"] != None:
        new_sentence[-1]["misc"] = 'SpaceAfter=No'
    

    new_sentence.append({'id': token_id, 
                         'form': item["part"], 
                         'lemma': sentence[i]['lemma'], # Lemma is in unsplit token
                         'upos': 'VERB', 
                         'xpos': 'Verb', 
                         'feats': feats[0], 
                         'head': sentence[i]['head'], 
                         'deprel': sentence[i]['deprel'], 
                         'deps': None, 
                         'misc': None})


    new_sentence.append({'id': token_id+1, 
                         'form': cop, 
                         'lemma': 'i', 
                         'upos': 'AUX', 
                         'xpos': 'Zero', 
                         'feats': feats[1], 
                         'head': token_id, 
                         'deprel': 'cop', 
                         'deps': None, 
                         'misc': None})


def main():

    Tk().withdraw() 
    filename = askopenfilename() 

    data = open(file_name,"r", encoding="utf-8").read()

    items = []

    for precop, var in forms.items():
        
        for variation, feats in var.items():

            # Match with copula and features
            raw = variation.split("+")
            raw[0]= r"(\w{2,}" # participle part
            raw[1] = "" + raw[1]
            raw[2] = ")(" + raw[2] 
            variation = REGEX_COP.format(r"".join(raw))
            variation += "\w+\\tVERB" # only verbal predicates

            info_copula = re.findall(variation,data) 

            for line, word, part ,cop, pers in info_copula:
                
                features = copy.deepcopy(feats)
                for person_s, (Number, Person) in person.items():
                    if re.fullmatch(person_s,pers) != None:
                        
                        features[1] = features[1].format(Number,Person) # check if proper predicate agreement

                        items.append({"line": line, # line_id
                                    "word": word, # whole token
                                    "part": part, # Participle form
                                    "feats": features, # Pre-determined feature
                                    "cop": cop} # copula form
                                    )
                        break

    for item in items:
    
        line = item["line"] # line_id
        word = item["word"] # word form
        feats = item["feats"] # features
        cop = item["cop"] # copula suffix

        REGEX_COPBLOCK = f"# sent_id = (\w+_\d+)((?:.*\\n){{{str(int(line))},{str(int(line)+5)}}})(?={line}\\t{word})"
        try:
            ID = re.search(REGEX_COPBLOCK, data).group(1)
        except:
            continue

        # Whole sentence block
        block = re.search(REGEX_BLOCK.format(ID), data).group(0)
        # Sentence metadata
        metadata = re.search(REGEX_BLOCK.format(ID), data).group(1)

        sentence = conllu.parse(block)[0]

        token_id = int(line)
        token_index = int(line)-1 # token index sentence list
        new_sentence = []
        cop_seen = cop2_seen = False

        for i in range(len(sentence)):
            
            # Fixes iterated heads
            fix_head(sentence[i], token_id)

            if check_split(sentence[i]) and cop_seen:
                sentence[i]["id"] =(sentence[i]["id"][0] + 1,'-',sentence[i]["id"][2] + 1)
                new_sentence.append(sentence[i])
                continue

            if check_split(sentence[i]):
                new_sentence.append(sentence[i])
                token_index += 1
                continue

            if cop_seen:
                hold = sentence[i]
                hold["id"] += 1            
                new_sentence.append(hold)

            if i == token_index:
                copula_split(sentence,new_sentence, i)
                cop_seen = True

            if not cop_seen:
                new_sentence.append(sentence[i])

        
        new_sentence = str(metadata + TokenList(new_sentence).serialize())

        f_out = open(file_name, "w", encoding="utf-8")

        data = re.sub(REGEX_BLOCK.format(ID),new_sentence, data)
        data = re.sub(r'SpacesAfter=\n', r'SpacesAfter=\\n', data)

        f_out.write(data)
        f_out.close()

if __name__ == "__main__":
    main()