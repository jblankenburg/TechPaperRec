# clean the data!!!!

import re
import gensim
from gensim.models import Doc2Vec
import gensim.models.doc2vec
from gensim.models.doc2vec import TaggedDocument
from collections import OrderedDict
import multiprocessing
import cPickle as pickle
from datetime import datetime
import random
import os
import sys

# os.system("taskset -p 0xff %d" % os.getpid())


# ------------------------------------------------------

def reorganizeData(categories, dataset):

    allTitles        = [] # Will hold all docs in original order
    allAbstracts     = [] # Will hold all docs in original order
    allRelatedWorks  = [] # Will hold all docs in original order
    allIntroductions = [] # Will hold all docs in original order
    allMethodology   = [] # Will hold all docs in original order
    allDiscussions   = [] # Will hold all docs in original order
    allConclusions  = [] # Will hold all docs in original order
    docs = {'title': allTitles, 'abstract': allAbstracts, 'introduction': allIntroductions, 'related work': allRelatedWorks,  'methodology': allMethodology, 'discussion': allDiscussions, 'conclusion': allConclusions }
    # docsTest = {'title': allTitles, 'abstract': allAbstracts, 'introduction': allIntroductions, 'related work': allRelatedWorks,  'methodology': allMethodology, 'discussion': allDiscussions, 'conclusion': allConclusions }
    # docsTrain = {'title': allTitles, 'abstract': allAbstracts, 'introduction': allIntroductions, 'related work': allRelatedWorks,  'methodology': allMethodology, 'discussion': allDiscussions, 'conclusion': allConclusions }

    counts = {'automata': 0, 'compilers': 0, 'CV': 0, 'graphics': 0, 'ML': 0, 'networking': 0, 'Parallel': 0, 'Robotics': 0, 'Security': 0, 'SoftwareEngineering': 0}

    # get keys
    cat2tag = {'automata': [], 'compilers': [], 'CV': [], 'graphics': [], 'ML': [], 'networking': [], 'Parallel': [], 'Robotics': [], 'Security': [], 'SoftwareEngineering': []}
    doc2tag = {}
    # doc2tagTest = {}

    # need to offset new samples with their own tags!!!!!
    if dataset == 'test':
        indx = -1 + 100
    else:
        indx = -1

    for key in categories:
        # keys = categories[key].keys()
        # print keys
        m = re.search(r'[0-9]+', key)
        indx += 1

        # /home/janelle/Documents/classes/complexNetworks/paper/DATASET/texfiles/automata/
        # 62 is offset to name
        offset = 64 + len(dataset)
        topic = getTopic(key[offset:])

        print topic
        counts[topic] += 1

        for cat in categories[key]:

            # For each doc, create a TaggedDocument from each category
            # Goal: Each TaggedDoc set will be one cat for all docs in dataset
            words = []
            tags  = []
            for token_no, token in enumerate(categories[key][cat]):
                # already tokenized here....
                # print line_no, line
                words.append(gensim.utils.to_unicode(token))
                # tags.append(int(m.group(0)))
            tags.append(indx)
            # print words
            # print tags
            # determine which list to append doc to
            doc_str = getDocList(cat)

            # TaggedDocument(words, tags)
            # docs[doc_str].append(TaggedDocument(words, tags))
            # NOTE: So this just has each separate methodology and discussion sections
            #       as their own tagged document.... need to instead combine these sections if possible?!?
            #       but won't array length still be an issue!?!??!
            # so.....lets see what happens if its this way first.........

            # train
            # if counts[topic] <= 10:
            docs[doc_str].append(TaggedDocument(words, tags))
            print 'topic: {} counts: {}'.format(topic, counts[topic])
            # need to save mapping from docids to indx!
            print m.group(0)
            doc2tag[indx] = m.group(0)
            cat2tag[topic].append(indx)

            # # test
            # else:
            #     docsTest[doc_str].append(TaggedDocument(words, tags))
            #     print 'TEST: topic: {} counts: {}'.format(topic, counts[topic])
            #     # need to save mapping from docids to indx!
            #     doc2tagTest[indx] = m.group(0)


    # return (docs, docsTrain, docsTest, doc2tagTrain, doc2tagTest)
    return (docs, doc2tag, cat2tag)

# -----------------------------------------

def getTopic(key):

    print key

    m = re.search(r'[\w]*\/', key)
    print m.group(0)


    if m.group(0) == 'automata/':
        return 'automata'

    if m.group(0) == 'compilers/':
        return 'compilers'

    if m.group(0) == 'CV/':
        return 'CV'

    if m.group(0) == 'graphics/':
        return 'graphics'

    if m.group(0) == 'ML/':
        return 'ML'

    if m.group(0) == 'networking/':
        return 'networking'

    if m.group(0) == 'Parallel/':
        return 'Parallel'

    if m.group(0) == 'Robotics/':
        return 'Robotics'

    if m.group(0) == 'Security/':
        return 'Security'

    if m.group(0) == 'SoftwareEngineering/':
        return 'SoftwareEngineering'

    return "error: key was {}".count(m.group(0))


# ------------------------------------------------------

def getDocList(cat):

    # title
    if re.match(r'[\s]*title[.]*',cat) != None:
        # print 'returned title'
        return 'title'

    # abstract
    elif re.match(r'[\s]*abstract[.]*',cat) != None:
        # print 'returned abstract'
        return 'abstract'

    # related work
    elif re.match(r'[\s]*related work[.]*',cat) != None:
        # print 'returned related work'
        return 'related work'

    # introduction
    elif re.match(r'[\s]*introduction[.]*',cat) != None:
        # print 'returned introduction'
        return 'introduction'

    # methodology
    elif re.match(r'[\s]*methodology[.]*',cat) != None:
        # print 'returned methodology'
        return 'methodology'

    # discussion
    elif re.match(r'[\s]*discussion[.]*',cat) != None:
        # print 'returned discussion'
        return 'discussion'

    # conclusion
    elif re.match(r'[\s]*conclusion[.]*',cat) != None:
        # print 'returned conclusion'
        return 'conclusion'



    return 'ERROR: key was {}'.format(cat)


# ------------------------------------------------------


# --------------------------------------------------------------
#  main
# --------------------------------------------------------------

def main():

    # NOTE: dataset should be set as "training" or "test"
    dataset = sys.argv[1]

    # open file
    fname = "cleaned_" + dataset + ".p"
    categories = pickle.load( open(fname, "r"))

    #  reorganize data:
    # (docs, docsTrain, docsTest, doc2tagTrain, doc2tagTest) = reorganizeData(categories)
    (docs, doc2tag, cat2tag) = reorganizeData(categories, dataset)

    # save the data back out
    fname = "reorganized_cat2tag_" + dataset + ".p"
    pickle.dump(cat2tag, open(fname, "w"))
    fname = "reorganized_doc2tag_" + dataset + ".p"
    pickle.dump(doc2tag, open(fname, "w"))
    # pickle.dump(doc2tagTest, open("test_docToTagTest.p", "w"))
    # pickle.dump(docs, open("test_organize_full.p", "w"))
    fname = "reorganized_docs_" + dataset + ".p"
    pickle.dump(docs, open(fname, "w"))
    # pickle.dump(docsTest, open("test_organize_test.p", "w"))


    print len(doc2tag)
    # print len(doc2tagTest)
    
    print 'done!'


# --------------------------------------------------------------
#  run main
# --------------------------------------------------------------

if __name__ == "__main__":
    startTime = datetime.now()
    main()
    print datetime.now() - startTime   
