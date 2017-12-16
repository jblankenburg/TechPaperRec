# clean the data!!!!

import re
import gensim
import cPickle as pickle
from datetime import datetime
import sys

# --------------------------------------------------------------

# define print function
def printCats(categories):
    # for cat in cats:
    #     print cat
    #     print cats[cat][0:100]
    #     print "\n---------------------------------------------------\n"

    for key in categories:
        for cat in categories[key]:
            print cat
            print categories[key][cat][:200]

# --------------------------------------------------------------

# define clean function
def cleanData(categories):

    # go through each category
    count = 0
    for key in categories:

        count += 1
        print key
        print count

        for cat in categories[key]:

            # if cat != 'discussion':


                # # manually cleaning
                categories[key][cat] = cleanMan(cat, categories[key][cat])

                # normalize text
                categories[key][cat] = normalize_text(categories[key][cat])

                # # gensim cleaning
                categories[key][cat] = cleanGen(cat, categories[key][cat])

    return categories

# --------------------------------------------------------------

# define manual clean function
def cleanMan(cat, data):

    print cat

    # things to remove:
    #  backslash:       r'\\\\'
    #  linecomment:     r'%'
    #  percent signs:   r'\\\%'
    #  commentEnv:      r'\\begin\s*{\s*comment\s*}'
    #  verbatimEnv:     r'\\begin\s*{\s*verbatim\s*}'
    #  newlines:        r'\n'
    #  endcomment:      r'\\end\s*{\s*comment\s*}'
    #  extra whitespace be replaced with a single space


    # data = '\medskip this is a test \subsection{asd}. this is a test \paragraph{asd}. this is a test \\cite{asd}. this is a test \\textit{asd}. this is a test \\textbf{asd}. this is a test \\ref{asd}. this is a test \\begin{asd}. this is a test \\end{a sd}. this is a test ~ } *this is a test \\footnote{a\tsd}. asdfasdf{}'
    # print data

    #  subsection:      r'\\subsection\s*\{'
    data = removeRE(r'\\subsection[\s|\*]*\{', data)

    #  paragraph:       r'\\paragraph\s*\{'
    data = removeRE(r'\\paragraph[\s|\*]*\{', data)

    #  cite:            r'\\cite\{[\w| ]*\}'
    data = removeRE(r'\\cite\{[^\}]*\}', data)

    #  textit:          r'\\textit\{'
    data = removeRE(r'\\textit\{', data)

    #  textbf:          r'\\textbf\{'
    data = removeRE(r'\\textbf\{', data)

    #  ref:             r'\\ref{[\w| ]*\}'
    data = removeRE(r'\\ref{[^\}]*\}', data)

    #  begin{*}:        r'\\begin\{[\w| ]*\}'
    data = removeRE(r'\\begin{[^\}]*\}', data)

    #  end{*}:      r'\\end\{[\w| ]*\}'
    data = removeRE(r'\\end{[^\}]*\}', data)

    #  footnote{*}:     r'\\footnote\{[\w|\s]*\}'
    data = removeRE(r'\\footnote{[^\}]*\}', data)

    #  skips:       r'\\[\w]*skip'
    data = removeRE(r'\\[\w]*skip', data)

    #  url{*}:      r'\\url\{[\w|\s]*\}'
    data = removeRE(r'\\url{[^\}]*\}', data)


    #  symbols:         [~,},*]
    data = removeRE(r'\~', data)
    data = removeRE(r'\}', data)
    data = removeRE(r'\*', data)
    data = removeRE(r'\$', data)
    data = removeRE(r'\%', data)


    # print data

    return data

# --------------------------------------------------------------

# define findRe function
def removeRE(pattern, data):

    numChars = 0
    for m in re.finditer(pattern, data):
        if m != []:
            # print '%02d-%02d: %s' % (m.start(), m.end(), m.group(0))
            data = data[:m.start() - numChars] + data[m.end() - numChars:]
            numChars = numChars + m.end()-m.start()

    return data

# --------------------------------------------------------------

# Convert text to lower-case and strip punctuation/symbols from words
def normalize_text(text):
    norm_text = text.lower()
    # Replace breaks with spaces
    norm_text = norm_text.replace('\\t', ' ')
    # Pad punctuation with spaces on both sides
    for char in ['.', '"', ',', '(', ')', '!', '?', ';', ':']:
        norm_text = norm_text.replace(char, ' ' + char + ' ')
    return norm_text

# --------------------------------------------------------------

# define gensim util clean function
def cleanGen(cat, data):

    # data = '\medskip this is a test \subsection{asd}. this is a test \paragraph{asd}. this is a test \\cite{asd}. this is a test \\textit{asd}. this is a test \\textbf{asd}. this is a test \\ref{asd}. this is a test \\begin{asd}. this is a test \\end{a sd}. this is a test ~ } *this is a test \\footnote{a\tsd}. asdfasdf{}'
    # print data

    data = gensim.utils.simple_preprocess(data)

    return data

# --------------------------------------------------------------


# --------------------------------------------------------------
#  main
# --------------------------------------------------------------

def main():

    # NOTE: dataset should be set as "training" or "test"
    dataset = sys.argv[1]
    
    # open file
    fname = "parsed_" + dataset + ".p"
    categories = pickle.load( open(fname, "r"))

    # clean the data
    categories = cleanData(categories)

    printCats(categories)

    # # detect phrases
    # for key in categories:
    #     for cat in categories[key]:
    #         print cat
    #         phrases = gensim.models.Phrases(categories[key][cat])
    #         print(phrases[categories[key][cat]])
    # # TODO: Fix and Save theseeeee
    #       For example. complex_network should be created byt it isnt!!!!

    # save the data back out
    fname = "cleaned_"+ dataset + ".p"
    pickle.dump(categories, open(fname, "w"))


    print 'done!'


# --------------------------------------------------------------
#  run main
# --------------------------------------------------------------

if __name__ == "__main__":
    startTime = datetime.now()
    main()
    print datetime.now() - startTime   

