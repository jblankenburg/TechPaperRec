# clean the data!!!!

import re
import gensim
from gensim.models import Doc2Vec
import gensim.models.doc2vec
from gensim.models.doc2vec import TaggedDocument
# from gensim.test.test_doc2vec import ConcatenatedDoc2Vec
from collections import OrderedDict
import multiprocessing
import cPickle as pickle
from datetime import datetime
import random
import os

# os.system("taskset -p 0xff %d" % os.getpid())

# --------------------------------------------------------------

# define print function
def printCats(categories):
    for key in categories:
        for cat in categories[key]:
            print cat
            print categories[key][cat][:200]



# --------------------------------------------------------------

# define print function
def trainModels(docs):

    models = {}

    # train word2vec models (keywords) <-- not working so far.......


    # train doc2vec models (one per category)
    cat_models = trainCatModels(docs)

    return models

# --------------------------------------------------------------

# define train doc2vec models for each category
def trainCatModels(docs):

    # set up model stuffs
    cores = multiprocessing.cpu_count()
    assert gensim.models.doc2vec.FAST_VERSION > -1, "This will be painfully slow otherwise"
    # print gensim.models.word2vec.FAST_VERSION 
    VOC_SIZE = 10000

    # train models - one per category
    for key in docs:

        print key

        # TODO: Test one key only for now!!!
        if key == 'title':
            # model = gensim.models.doc2vec.Doc2Vec(size=5, min_count=5, iter=55, workers=cores)
            # model = gensim.models.doc2vec.Doc2Vec(size=5, min_count=1, workers=cores)
            # simple_models = [gensim.models.doc2vec.Doc2Vec(size=5, min_count=1, workers=cores)]

            # print len(docs[key])
            # print docs[key]

            simple_models = [
                # # PV-DM w/ concatenation - window=5 (both sides) approximates paper's 10-word total window size
                # Doc2Vec(dm=1, dm_concat=1, size=5, window=10, hs=0, min_count=1, iter=10, workers=cores),
                # # PV-DBOW 
                # Doc2Vec(dm=0, size=5, hs=0, min_count=1, iter=10, workers=cores),
                # # PV-DM w/ average
                # Doc2Vec(dm=1, dm_mean=1, size=5, window=10, hs=0, min_count=1, iter=10, workers=cores),

                # Doc2Vec(dm=1, dm_concat=1, size=5,  negative=5, hs=0, min_count=1, window=5, iter=10, workers=cores, max_vocab_size=VOC_SIZE),
                # Doc2Vec(dm=0, size=5,  negative=5, hs=0, min_count=1, window=5, iter=10, workers=cores, max_vocab_size=VOC_SIZE),
                # Doc2Vec(dm=1, dm_mean=1, size=5,  negative=5, hs=0, min_count=1, window=5, iter=10, workers=cores, max_vocab_size=VOC_SIZE),

                Doc2Vec(dm=1, dm_concat=1, size=5,  negative=0, hs=0, min_count=2, window=5, iter=10, workers=cores, max_vocab_size=VOC_SIZE),
                Doc2Vec(dm=0, size=5,  negative=0, hs=0, min_count=2, window=5, iter=10, workers=cores, max_vocab_size=VOC_SIZE),
                Doc2Vec(dm=1, dm_mean=1, size=5,  negative=0, hs=0, min_count=2, window=5, iter=10, workers=cores, max_vocab_size=VOC_SIZE),
                ]
        # else:
        #     # define models
        #     simple_models = [
        #         # PV-DM w/ concatenation - window=5 (both sides) approximates paper's 10-word total window size
        #         Doc2Vec(dm=1, dm_concat=1, size=100, window=10, hs=0, min_count=2, iter=10, workers=cores, max_vocab_size=VOC_SIZE),
        #         # PV-DBOW 
        #         Doc2Vec(dm=0, size=100, hs=0, min_count=2, iter=10, workers=cores, max_vocab_size=VOC_SIZE),
        #         # PV-DM w/ average
        #         Doc2Vec(dm=1, dm_mean=1, size=100, window=10, negative=5, hs=0, min_count=2, iter=10, workers=cores, max_vocab_size=VOC_SIZE),
        #         ]

            # for item in docs[key]:
            #     print item.tags


            print simple_models[0].estimate_memory(vocab_size=VOC_SIZE)
            print simple_models[0].scan_vocab(docs[key])
            print len(simple_models[0].wv.vocab)
            print simple_models[0].scale_vocab(min_count = 1, dry_run=True)
            print len(simple_models[0].wv.vocab)
            # print simple_models[0].finalize_vocab()            
            # print len(simple_models[0].wv.vocab)

        # # Speed up setup by sharing results of the 1st model's vocabulary scan
        # startTimeVocab = datetime.now()
        # print 'starting to build vocab: {}'.format(startTimeVocab)
        # simple_models[0].build_vocab(doc)  # PV-DM w/ concat requires one special NULL word so it serves as template
  
        # # simple_models[0] = Doc2Vec.load('doc2vec_title_VOCAB.model')

        # print 'vocab was built in {}\n'.format(datetime.now() - startTimeVocab)
        # print len(simple_models[0].wv.vocab)

        # startTimeVocab = datetime.now()
        # print 'starting to save vocab model: {}'.format(startTimeVocab)
        # simple_models[0].save("doc2vec_{}_VOCAB_8.model".format(key))
        # print 'saved vocab model in {}\n'.format(datetime.now() - startTimeVocab)

        # print(simple_models[0])
        # for model in simple_models[1:]:
        #     model.reset_from(simple_models[0])
        #     print(model)
        # models_by_name = OrderedDict((str(model), model) for model in simple_models)

        # # NOT WORKING, IMPORT ERROR, try later if other models not sufficient
        # # models_by_name['dbow+dmm'] = ConcatenatedDoc2Vec([simple_models[1], simple_models[2]])
        # # models_by_name['dbow+dmc'] = ConcatenatedDoc2Vec([simple_models[1], simple_models[0]])

        # # print 'starting to build vocab'
        # # startTimeVocab = datetime.now()
        # # model.build_vocab(doc)
        # # print 'vocab was built in {}\n'.format(datetime.now() - startTimeVocab)

        # # print model['domains']

        # for name, train_model in models_by_name.items():
        #     print 'starting to train model: {}'.format(name)
        #     startTimeModel = datetime.now()
        #     model.train(doc, total_examples=model.corpus_count, epochs=model.iter)
        #     print 'model was trained in {}\n'.format(datetime.now() - startTimeModel)

        #     model.save("doc2vec_{}_{}.model".format(key,name))
        #     print "model was saved to: doc2vec_{}_{}.model".format(key,name)


        # # print 'starting to train model'
        # # startTimeModel = datetime.now()
        # # model.train(doc, total_examples=model.corpus_count, epochs=model.iter)
        # # print 'model was trained in {}\n'.format(datetime.now() - startTimeModel)


        # # model.save("doc2vec_{}.model".format(key))
        # # print "model was saved to: doc2vec_{}.model".format(key)

        else:
            print 'skip {}'.format(key)

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

    # open file - this is 2.6 GB of memory... if it comes down to it then maybe breeak file into different categories and only load in one at a time?!?
    docsTrain = pickle.load( open("test_organize_train.p", "r"))

    # while(1):
    #     print '.'

    # print data
    # printCats(categories)

    # train models:
    models = trainModels(docsTrain)

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
