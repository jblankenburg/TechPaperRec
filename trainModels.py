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

# --------------------------------------------------------------

# define print function
def printCats(categories):
    for key in categories:
        for cat in categories[key]:
            print cat
            print categories[key][cat][:200]



# --------------------------------------------------------------

# define print function
def trainModels(categories):

    models = {}

    # train word2vec models (keywords)


    # train doc2vec models (one per category)
    cat_models = trainCatModels(categories)

    return models

# --------------------------------------------------------------

# define train doc2vec models for each category
def trainCatModels(categories):

    # set up model stuffs
    cores = multiprocessing.cpu_count()
    assert gensim.models.doc2vec.FAST_VERSION > -1

    simple_models = [
        # PV-DM w/ concatenation - window=5 (both sides) approximates paper's 10-word total window size
        Doc2Vec(dm=1, dm_concat=1, size=100, window=5, negative=5, hs=0, min_count=2, workers=cores),
        # PV-DBOW 
        Doc2Vec(dm=0, size=100, negative=5, hs=0, min_count=2, workers=cores),
        # PV-DM w/ average
        Doc2Vec(dm=1, dm_mean=1, size=100, window=10, negative=5, hs=0, min_count=2, workers=cores),
        ]


    # Speed up setup by sharing results of the 1st model's vocabulary scan
    simple_models[0].build_vocab(alldocs)  # PV-DM w/ concat requires one special NULL word so it serves as template
    print(simple_models[0])
    for model in simple_models[1:]:
        model.reset_from(simple_models[0])
        print(model)

    models_by_name = OrderedDict((str(model), model) for model in simple_models)


# ------------------------------------------------------

def reorganizeData(categories):

    allTitles        = [] # Will hold all docs in original order
    allAbstracts     = [] # Will hold all docs in original order
    allRelatedWorks  = [] # Will hold all docs in original order
    allIntroductions = [] # Will hold all docs in original order
    allMethodology   = [] # Will hold all docs in original order
    allDiscussions   = [] # Will hold all docs in original order
    allConclusions  = [] # Will hold all docs in original order
    docs = {'title': allTitles, 'abstract': allAbstracts, 'introduction': allIntroductions, 'related work': allRelatedWorks,  'methodology': allMethodology, 'discussion': allDiscussions, 'conclusion': allConclusions }

    # get keys
    for key in categories:
        # keys = categories[key].keys()
        # print keys
        m = re.search(r'[0-9]+', key)

        for cat in categories[key]:

            # For each doc, create a TaggedDocument from each category
            # Goal: Each TaggedDoc set will be one cat for all docs in dataset
            words = []
            tags  = []
            for token_no, token in enumerate(categories[key][cat]):
                # already tokenized here....
                # print line_no, line
                words.append(gensim.utils.to_unicode(token))
                tags.append(int(m.group(0)))
            # print words
            # print tags
            # determine which list to append doc to
            doc_str = getDocList(cat)

            # TaggedDocument(words, tags)
            docs[doc_str].append(TaggedDocument(words, tags))
            # NOTE: So this just has each separate methodology and discussion sections
            #       as their own tagged document.... need to instead combine these sections if possible?!?
            #       but won't array length still be an issue!?!??!


    # print allTitles
    # print allMethodology
    # print allDiscussions


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

    # open file
    categories = pickle.load( open("test_clean.p", "r"))

    # print data
    # printCats(categories)

    #  reorganize data:
    reorganizeData(categories)



    # train models:
    # models = trainModels(categories)

    # save the data back out
    # pickle.dump(categories, open("test_clean.p", "w"))


    print 'done!'


# --------------------------------------------------------------
#  run main
# --------------------------------------------------------------

if __name__ == "__main__":
    startTime = datetime.now()
    main()
    print datetime.now() - startTime   
