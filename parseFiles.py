# import things!
import os
import re
import cPickle as pickle
from datetime import datetime
import sys

# --------------------------------------------------------------
#  functions
# --------------------------------------------------------------

# --------------------------------------------------------------

# Define function for getting list of all files to parse
def getFiles(base_path, files):
    for (dirpath, dirnames, filenames) in os.walk(base_path):
        for f in filenames:
            if f.endswith(".tex"):
                temp = os.path.join(dirpath, f)
                files.append(temp)
                
    return files


# --------------------------------------------------------------

#  Define function for getting content from ONE file
def getContent(file):
    f = open(file, "r")
    content = f.readlines()
    content = [x.replace('\n', ' ') for x in content]
    return content

# --------------------------------------------------------------

# Define function for getting the \section names from file
def getSections(content):
    names = {}
    for line in content:
        temp = []

        # ignore all sections in the appendix!
        valApp = line.find('\\appendix') #TODO: Make sure no papers ref "appendix"
        if valApp != -1:
            return names
        # ignore all sections in the appendix!
        valApp = line.find('\\appendices') #TODO: Make sure no papers ref "appendices"
        if valApp != -1:
            return names
        # ignore the bibliograph
        if re.match(r'[ |\t]*\\begin\{[a-z]*bibliography\}', line) != None:
            return names

        # TODO: What it is chapters instead of Sections?!?!
        # Find chapters?
        val = line.find('\\chapter')
        if val != -1:

            if line[val+9] == '}':
                print "\nChapter was ignored because not real section! It is \section}\n"
            else:
                # flag = 0
                # # extract section names
                # for char in line:
                #     if char == '}':
                #         flag = 0
                #     if flag == 1:
                #         temp.append(char)
                #     if char == '{':
                #         flag = 1
                temp = re.search(r'\{[\w| ]*\}', line)
                if temp != None:
                    # print temp
                    name = ''.join(temp)
                else:
                    name = ''

                # save names of the sections
                names[name] = ''

        # find sections
        val = line.find('\\section')
        if val != -1:

            if len(line) > val + 9: 

                if line[val+9] == '}':
                    print "\nSection was ignored because not real section! It is \section}\n"
                else:
                    # flag = 0
                    # # extract section names
                    # for char in line:
                    #     if char == '}':
                    #         flag = 0
                    #     if flag == 1:
                    #         temp.append(char)
                    #     if char == '{':
                    #         flag = 1
                    temp = re.search(r'\{[\w| ]*\}', line)
                    if temp != None:
                        # print temp.group(0)
                        name = ''.join(temp.group(0))
                    else:
                        name = ''
                        
                    # save names of the sections
                    names[name] = ''
            
    return names
                    
# --------------------------------------------------------------

#  Define function to loop through section names and fill in sections
def fillSections(names, content):
    for name in names:
        flag = 0
        temp = []
        count = 0
        for line in content:
            count += 1
            # only get lines up until appendix
            if re.match(r'[ |\t]*\\appendix',line) != None:
                # return names #### Can't return names here becuase inside for loop!!!! so how to go to next instance of for loop instead?!?!
                # print 't1'
                break
            elif re.match(r'[ |\t]*\\appendices',line) != None:
                # return names
                break 
            # dont include anything after the bibliography
            elif re.match(r'[ |\t]*\\begin\{[a-z]*bibliography\}', line) != None:
                break

            else:            
                # fill in sections
                val = line.find(name)
                if val != -1:
                    # print('ZZZZZZZZZ\n1\nZZZZZZZZZZZZZZZZ')
                    flag = 1
                    val2 = line.find('}')
                    temp.append(line[(val2+1):])
                    continue

                val3 = line.find('\\section')
                val4 = line.find('\\chapter')
                if val3 != -1 or val4 != -1:
                    flag = 0
                if flag == 1:
                    if lineOkay(line):
                        temp.append(line.lstrip())
                    # only add lines if not comments
                    # if line != '':
                    #     if line[0] != '%':
                    #         temp.append(line)
                continue
            # print 't2'
            break

        names[name] = ''.join(temp)

    return names

# --------------------------------------------------------------


# Define function to fill in abstract
def lineOkay(line):

    # need to get rid of: Comments, \being{figure}[.], \end{figure}, \includegraphics, 

    if line != '':
        # only add lines if not comments
        if re.match(r'[ |\t]*%', line) == None:
            # only if not begin figure
            # if re.match(r'\\begin\{figure\}\[.*\]',test) == None
            if re.match(r'[ |\t]*\\begin\{figure[\*]*\}',line) == None:
                # only if not end figure
                if re.match(r'[ |\t]*\\end\{figure\[\*]*}',line) == None:
                    # only if not include graphics
                    if re.match(r'[ |\t]*\\includegraphics',line) == None:
                        # only if not include graphics
                        if re.match(r'[ |\t]*\\label',line) == None:
                            if re.match(r'[ |\t]*\\centering',line) == None:
                                if re.match(r'[ |\t]*\\subfloat',line) == None:
                                    return True
    return False


# --------------------------------------------------------------

# Define function to fill in abstract
def fillAbstract(names, content):
    flag = 0
    temp = []
    for line in content:
        val = line.find('n{abstract}')
        if val != -1:
            flag = 1
            val2 = line.find('}')
            temp.append(line[(val2+1):])
            continue
        val3 = line.find('d{abstract}')
        if val3 != -1:
            flag = 0
        if flag == 1:
            if line != '':
                if line[0] != '%':
                    temp.append(line)
    names['abstract'] = ''.join(temp)
    return names

# --------------------------------------------------------------

# Define function to fill in title:
def fillTitle(names, content):
    flag = 0
    temp = []
    for line in content:
        val = line.find('\\title{')
        if val != -1:
            flag = 1
            val2 = line.find('}')
            temp.append(line[(val+7):(val2)])
            names['title'] = ''.join(temp)
            return names

# --------------------------------------------------------------

def fillNamesDict(names, content):
    names = fillSections(names, content)
    names = fillAbstract(names, content)
    names = fillTitle(names, content)
    return names

# --------------------------------------------------------------

def printNamesDict(names):
    for name in names:
        print name
        print names[name]
        print '\n----------------------------------------------\n'

# --------------------------------------------------------------

def convertNamesToCats(names, cats):

    # --------------------------------------------
    # TODO: The issue here is that order is not preserved, so if multiple things go in one category, the ordering is wrong so how much will this matter?!!?!?
    # --------------------------------------------


    # define the synonyms for categorization
    syn_intro = ['introduction']
    syn_relWork = ['related work', 'background']
    syn_meth = ['methodology', ] # TODO: Fix this, this should be all others
    syn_disc = ['discussion', 'results', 'experiment', 'implementation'] # TODOL What if dicussion and conclusion!?!?
    syn_conc = ['conclusion', 'future work', 'limitations', 'remarks']
    syn_ignore = ['acknowledgments']

    # loop through names and put into correct cat:
    count = 0
    discCount = 0
    for name in names:

        # check title
        if name == 'title':
            cats['title'] = cats['title'].join(names[name])
            print "\n--------\nSection {} was added to Category {}!\n-------\n".format(name, 'title')
            print cats['title']

        # check abstract
        elif name == 'abstract':
            cats['abstract'] = cats['abstract'].join(names[name])
            print "\n--------\nSection {} was added to Category {}!\n-------\n".format(name, 'abstract')
            # print cats['abstract']

        # check other sections:
        else:

            # set flag to see if name is found in anything but method syns
            found = 0

            # check intro
            (cats, found) = checkSyn(syn_intro, found, name, 'introduction', cats, names)

            # check related work
            (cats, found) = checkSyn(syn_relWork, found, name, 'related work', cats, names)

            # check discussion 
            (cats, found, discCount) = checkSynDisc(syn_disc, found, name, 'discussion', cats, names, discCount)

            # check conclusion
            (cats, found) = checkSyn(syn_conc, found, name, 'conclusion', cats, names)

            # if not found, then put into methodology
            if found == 0:
                
                # make sure its not in ignore list
                ignore = 0
                for syn in syn_ignore:
                    name_lower = name.lower()
                    val = name_lower.find(syn)
                    if val != -1:
                        ignore = ignore | 1
                        print "\n--------\nSection {} was ignored!\n-------\n".format(name)
                
                # if not in ignore list, then add to methodology
                if ignore == 0:
                    count += 1
                    # print cats['methodology']
                    # cats['methodology'] = cats['methodology'].join(names[name])  
                    temp_str = 'methodology_{}'.format(count)
                    cats[temp_str] = ''.join(names[name])
                    print "\n--------\nSection {} was added to Category {}!\n-------\n".format(name, temp_str)

    return cats       
        
# --------------------------------------------------------------

def checkSyn(syn_dict, found, name_str, cat_str, cats, names):
    
    # check syns
    added = 0
    for syn in syn_dict:
        name_str_lower = name_str.lower()
        val = name_str_lower.find(syn)
        if val == -1:
            found = found | 0
        else:
            if added == 0:
                cats[cat_str] = cats[cat_str].join(names[name_str])   
                print "\n--------\nSection {} was added to Category {}!\n-------\n".format(name_str, cat_str)
                found = found | 1
                added = 1
            
    return (cats, found)

# --------------------------------------------------------------

def checkSynDisc(syn_dict, found, name_str, cat_str, cats, names, discCount):
    
    # check syns
    added = 0
    for syn in syn_dict:
        name_str_lower = name_str.lower()
        val = name_str_lower.find(syn)
        if val == -1:
            found = found | 0
        else:
            if added == 0:
                discCount += 1
                temp_str = 'discussion_{}'.format(discCount)
                cats[temp_str] = ''.join(names[name_str])   
                print "\n--------\nSection {} was added to Category {}!\n-------\n".format(name_str, temp_str)
                found = found | 1
                added = 1
            
    return (cats, found, discCount)

# --------------------------------------------------------------

def printCats(cats):
    for cat in cats:
        print cat
        print cats[cat]
        print "\n---------------------------------------------------\n"

# --------------------------------------------------------------



# --------------------------------------------------------------
#  main
# --------------------------------------------------------------

def main():

    # define stuffs
    # base_path = "/home/janelle/Documents/classes/complexNetworks/paper/texfiles"

    # NOTE: dataset should be set as "training" or "test"
    dataset = sys.argv[1]

    base_path = "/home/janelle/Documents/classes/complexNetworks/paper/" + dataset +"/texfiles"
    files = []

    # test getting all files to parse
    files = getFiles(base_path, files)
    # files = ["/home/janelle/Documents/classes/complexNetworks/paper/texfiles/networking/tex/08092322.tex"]
    # files = ["/home/janelle/Documents/classes/complexNetworks/paper/texfiles/networking/tex/171011304.tex"]


    # loop through all the files and parse out the stuff!
    categories = {}

    for tfile in files:

        # ----------------
        # run stuff on one file:
        print tfile
        
        # get content
        content = getContent(tfile)

        # get sections
        names = getSections(content)

        # fill names dict with content from sections + abstract + title
        names = fillNamesDict(names, content)

        # print names with their content
        # printNamesDict(names)

        # define the categories dict
        cats = {'title':'','abstract':'','introduction':'','related work':'','methodology':'','discussion':'','conclusion':''}

        # convert from names to cats
        cats = convertNamesToCats(names, cats)

        # print cats
        # printCats(cats)

        # TODO: SAVE OFF CATS OR SOMETHING SO ITS NOT REWRITTEN EVERTTIME?!?!
        categories[tfile] = cats

        # Now remove the memory for cats and content and names?
        del cats
        del content
        del names

    fname = "parsed_" + dataset + ".p"
    pickle.dump(categories, open(fname, "w"))
    print 'done!'


# --------------------------------------------------------------
#  run main
# --------------------------------------------------------------

if __name__ == "__main__":
    startTime = datetime.now()
    main()
    print datetime.now() - startTime   

