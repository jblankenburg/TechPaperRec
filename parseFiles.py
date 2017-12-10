# import things!
import os
import cPickle as pickle


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
        
        # find sections
        val = line.find('\section')
        if val != -1:
            flag = 0
            # extract section names
            for char in line:
                if char == '}':
                    flag = 0
                if flag == 1:
                    temp.append(char)
                if char == '{':
                    flag = 1
                name = ''.join(temp)
                
            # save names of the sections
            names[name] = ''
            
    return names
                    
# --------------------------------------------------------------

#  Define function to loop through section names and fill in sections
def fillSections(names, content):
    for name in names:
        flag = 0
        temp = []
        for line in content:
            # fill in sections
            val = line.find(name)
            if val != -1:
                flag = 1
                val2 = line.find('}')
                temp.append(line[(val2+1):])
                continue
            val3 = line.find('\section')
            if val3 != -1:
                flag = 0
            if flag == 1:
                if line != '':
                    if line[0] != '%':
                        temp.append(line)
        names[name] = ''.join(temp)
        
    return names

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
        val = line.find('title{')
        if val != -1:
            flag = 1
            val2 = line.find('}')
            temp.append(line[(val+6):(val2+1)])
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
    syn_conc = ['conclusion', 'future work', 'limitations']
    syn_ignore = ['acknowledgments']

    # loop through names and put into correct cat:
    for name in names:

        # check title
        if name == 'title':
            cats['title'] = cats['title'].join(names[name])

        # check abstract
        elif name == 'abstract':
            cats['abstract'] = cats['abstract'].join(names[name])

        # check other sections:
        else:

            # set flag to see if name is found in anything but method syns
            found = 0

            # check intro
            (cats, found) = checkSyn(syn_intro, found, name, 'introduction', cats, names)

            # check related work
            (cats, found) = checkSyn(syn_relWork, found, name, 'related work', cats, names)

            # check discussion 
            (cats, found) = checkSyn(syn_disc, found, name, 'discussion', cats, names)

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
                    cats['methodology'] = cats['methodology'].join(names[name])  
                    print "\n--------\nSection {} was added to Category {}!\n-------\n".format(name, 'methodology')

    return cats       
        
# --------------------------------------------------------------

def checkSyn(syn_dict, found, name_str, cat_str, cats, names):
    
    # check syns
    for syn in syn_dict:
        name_str_lower = name_str.lower()
        val = name_str_lower.find(syn)
        if val == -1:
            found = found | 0
        else:
            cats[cat_str] = cats[cat_str].join(names[name_str])   
            print "\n--------\nSection {} was added to Category {}!\n-------\n".format(name_str, cat_str)
            found = found | 1
            
    return (cats, found)

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
	base_path = "/home/janelle/Documents/classes/complexNetworks/paper/texfiles"
	files = []

	# test getting all files to parse
	files = getFiles(base_path, files)
	# print files

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
	
	# pickle.dunp(categories, open("test.p", "wb"))
	print 'done!'


# --------------------------------------------------------------
#  run main
# --------------------------------------------------------------

if __name__ == "__main__":
    main()

