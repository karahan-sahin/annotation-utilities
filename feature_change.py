import re
import sys
from tkinter import Tk  
from tkinter.filedialog import askopenfilename

REGEX_POT = r'\b\w*(Pot)[^\W]\w*\b'
REGEX_AOR = r'Tense=Aor'
REGEX_PROSP = r'Aspect=Imp.+Tense=Fut'
REGEX_CLF = r'\t(.([^\t])+?)\t\d+\t(clf)'
REGEX_DET = r'.+?(ANum)\t([^\t]+?)\t(\d+)\tdet'

REGEX_EREK = r'\d+\t(\w{2,}[ea]r[ea]k)\t(\w+)\t(\w+)\t(\w+)\t(.+?)\t'
REGEX_IYOR = r'\d+\t(\w{2,}yor)\t(\w+)\t(\w+)\t(\w+)\t(.+?)\t'
REGEX_NEXISTP = r'(\d+)\t(var\w*)\tvar\t(\w+)\t(\w+)\t(.+?)\t'
REGEX_NEXISTN = r'(\d+)\t(yok\w*)\tyok\t(\w+)\t(\w+)\t(.+?)\t'

# That is problematic 
REGEX_DEGIL = r'(\d+)\tdeğil(\w*)\tdeğil\t(?!AUX)(\w+)\t(\w+)\t(.+?)\t'

REGEX_ISE = r'\d+\tise\ti\t(\w+)\t(\w+)\t(.+?)\t.+?\t(.+?)\t'
REGEX_MI = r'\d+\tm[ıiuü]\w*\tm[ıiuü]\t(\w+)\t(\w+)\t(.+?)\t.+?\t(.+?)\t'

Tk().withdraw() 
file_name = askopenfilename() 

data = open(f"{file_name}").read()

def pot_replace(term):

    print('Matched term feats: ', term.group(0))

    token = term.group(0)

    token = re.sub("Pot", "abil", token) # Fix Pot regex change

    print('Matched term fixed: ', token)
    print("---------------")

    return token

def aor_replace(term):

    print('Matched term feats: ', term.group(0))

    token = term.group(0)

    token = re.sub("Aor", "Pres", token) # Fix Tense

    print('Matched term fixed: ', token)
    print("---------------")

    return token

def prosp_replace(term):

    print('Matched term feats: ', term.group(0))

    token = term.group(0)

    token = re.sub("Imp", "Prosp", token) # Fix Aspect

    print('Matched term fixed: ', token)
    print("---------------")

    return token
 
def clf_replace(term):

    print('Matched term feats: ', term.group(0))

    token = term.group(0)
    token = re.sub(re.sub(r"\|",r"\|",term.group(1)), "Case=Nom|Number=Sing|Person=3", token) # Change features
    token = re.sub(term.group(3), "nmod", token) # Fix deprel

    print('Matched term fixed: ', token)
    print("---------------")


    return token

def det_replace(term):

    print('Matched term feats: ', term.group(0))

    token = term.group(0)
    # If bir marked as NUM, it has NumType feature
    if(term.group(2) != "NumType=Dist"):
        token = re.sub(term.group(1), "Det", token) # Fix XPOS
        token = re.sub(term.group(2), "_", token) # Set features as none

    print('Matched term fixed: ', token)
    print("---------------")

    return token

def erek_replace(term):

    # olarak ADP PCNom
    print('Matched term feats: ', term.group(0))

    token = term.group(0)

    if term.group(3) == "VERB":
        token = re.sub("Mood=Imp", "Aspect=Prog", token) # Fix Aspect
    else:
        print("No Change") # olarak ADP PCNom

    print('Matched term fixed: ', token)
    print("---------------")

    return token

def iyor_replace(term):

    print('Matched term feats: ', term.group(0))

    token = term.group(0)

    # If tagged as verb
    if term.group(3) == "VERB":
        token = re.sub("Aspect=Prog", "Aspect=Imp", term.group(0)) # Fix Aspect
    else:
        print("No Change")

    print('Matched term fixed: ', token)
    print("---------------")

    return token


def var_replace(term):

    print('Matched term feats: ', term.group(0)) # all
    
    token = term.group(0)

    # Check whether tagged as a Verb
    if term.group(3) != "VERB":
        token = re.sub(term.group(3), "NOUN", token) # Fix UPOS
        token = re.sub(term.group(4), "Exist", token) # Fix XPOS
        if re.search("Polarity=\w+",term.group(5)): # If has Polarity
            print("No Feature Change")
            print(term.group(5))
        else:
            token = re.sub(re.sub(r"\|",r"\|",term.group(5)),"Polarity=Pos",token) # Only Polarity feature

        print('Matched term fixed: ', token)
    else:
        print("No Change")
        

    print("---------------")

    return token

def yok_replace(term):

    print('Matched term feats: ', term.group(0)) # all
    
    token = term.group(0)

    if term.group(3) != "VERB":
        token = re.sub(term.group(3), "NOUN", token)
        token = re.sub(term.group(4), "Exist", token)
        if re.search("Polarity=\w+",term.group(5)):
            print(term.group(5))
        else:
            token = re.sub(re.sub(r"\|",r"\|",term.group(5)),"Polarity=Neg",token)

        print('Matched term fixed: ', token)
    else:
        print("No Feature Change")
        
    print("---------------")

    return token


def degil_replace(term):

    print('Matched term feats: ', term.group(0)) # all
    
    token = term.group(0)

    token = re.sub(term.group(3), "AUX", token) # Fix UPOS
    token = re.sub(term.group(4), "Overt", token) # Fix XPOS

    if re.search("Polarity=\w+",term.group(5)): # 
        pass
    else:
        print(term.group(5))


    print('Matched term fixed: ', token)
    print("---------------")

    return token


def ise_replace(term):

    print('Matched term feats: ', term.group(0))

    token = term.group(0)
    token = re.sub(term.group(1), "PART", token) # Fix UPOS
    token = re.sub(term.group(2), "Topic", token) # Fix XPOS
    token = re.sub(term.group(4), "discourse", token) # Fix deprel

    print('Matched term fixed: ', token)
    print("---------------")


    return token


def mi_replace(term):

    print('Matched term feats: ', term.group(0))

    token = term.group(0)

    token = re.sub(term.group(1), "PART", token) # Fix UPOS
    token = re.sub(term.group(2), "Ques", token) # Fix XPOS
    token = re.sub(term.group(4), "discourse:q", token) # Fix deprel

    print('Matched term fixed: ', token)
    print("---------------")

    return token


while (True):

    pot_fixed = re.sub(REGEX_POT,pot_replace,data)
    answer = input('Are you sure you want to change it? Y/n: ')
    if (answer == "Y"):
        data = pot_fixed
    elif (answer == "n"):
        pass
    
    aor_fixed = re.sub(REGEX_AOR,aor_replace,data)
    answer = input('Are you sure you want to change it? Y/n')
    if (answer == "Y"):
        data = aor_fixed
        print("Aor error fixed")
    elif (answer == "n"):
        pass

    prosp_fixed = re.sub(REGEX_PROSP,prosp_replace,data)
    answer = input('Are you sure you want to change it? Y/n')
    if (answer == "Y"):
        data = prosp_fixed
        print("Prosp feature fixed")
    elif (answer == "n"):
        pass

    
    clf_fixed = re.sub(REGEX_CLF,clf_replace,data)
    answer = input('Are you sure you want to change it? Y/n')
    if (answer == "Y"):
        data = clf_fixed
        print("clf features fixed")
    elif (answer == "n"):
        pass
    
    det_fixed = re.sub(REGEX_DET,det_replace,data)
    answer = input('Are you sure you want to change it? Y/n')
    if (answer == "Y"):
        data = det_fixed
        print("det features fixed")
    elif (answer == "n"):
        print("det features remains")
        pass

    erek_fixed = re.sub(REGEX_EREK,erek_replace,data)
    answer = input('Are you sure you want to change it? Y/n')
    if (answer == "Y"):
        data = erek_fixed
        print("erek features fixed")
    elif (answer == "n"):
        print("erek features remains")
        pass

    iyor_fixed = re.sub(REGEX_IYOR,iyor_replace,data)
    answer = input('Are you sure you want to change it? Y/n')
    if (answer == "Y"):
        data = iyor_fixed
        print("iyor features fixed")
    elif (answer == "n"):
        print("iyor features remains")
        pass
    

    var_fixed = re.sub(REGEX_NEXISTP,var_replace,data)
    answer = input('Are you sure you want to change it? Y/n')
    if (answer == "Y"):
        data = var_fixed
        print("var features fixed")
    elif (answer == "n"):
        print("var features remains")
        pass

    yok_fixed = re.sub(REGEX_NEXISTN,yok_replace,data)
    answer = input('Are you sure you want to change it? Y/n')
    if (answer == "Y"):
        data = yok_fixed
        print("yok features fixed")
    elif (answer == "n"):
        print("yok features remains")
        pass

    degil_fixed = re.sub(REGEX_DEGIL,degil_replace,data)
    answer = input('Are you sure you want to change it? Y/n')
    if (answer == "Y"):
        data = degil_fixed
        print("değil features fixed")
    elif (answer == "n"):
        print("değil features remains")
        pass
    
    ise_fixed = re.sub(REGEX_ISE,ise_replace,data)
    answer = input('Are you sure you want to change it? Y/n')
    if (answer == "Y"):
        data = ise_fixed
        print("ise features fixed")
    elif (answer == "n"):
        print("ise features remains")
        pass

    mi_fixed = re.sub(REGEX_MI,mi_replace,data)
    answer = input('Are you sure you want to change it? Y/n')
    if (answer == "Y"):
        data = mi_fixed
        print("mi features fixed")
    elif (answer == "n"):
        print("mi features remains")
        pass

    break

final_answer = input("Are you sure about these changes?Y/n")
if final_answer == "Y":
    output = open(f"{file_name}","w")  
    output.write(data)
    output.close()
else:
    pass