# clean the data!!!!

import re
import gensim
from gensim.models import Doc2Vec
import gensim.models.doc2vec
from gensim.models.doc2vec import TaggedDocument
import collections
from collections import OrderedDict
import multiprocessing
import cPickle as pickle
from datetime import datetime
import random
import os
import numpy as np
from IPython.display import HTML


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
def testModels(docs, doc2tag):

    models = {}

    # train word2vec models (keywords) <-- not working so far.......


    # train doc2vec models (one per category)
    cat_models = testCatModels(docs, doc2tag)

    for key in docs:
        items = cat_models[key]

        # # map from ranks to docid
        # for item in items:
        #     (rank, cn_rank, second_rank, cn_second_rank) = item
        #     print cn_rank
        #     # print doc2tag[rank]


    # TODO: placeholder
    models['cats'] = cat_models

    return models

# --------------------------------------------------------------

# define train doc2vec models for each category
def testCatModels(docs, doc2tag):

    data = {}

    # set up model stuffs
    cores = multiprocessing.cpu_count()
    assert gensim.models.doc2vec.FAST_VERSION > -1, "This will be painfully slow otherwise"
    print gensim.models.word2vec.FAST_VERSION 

    # train models - one per category
    for key in docs:

        # TODO: Test one key only for now!!!
        # if key == 'title':


            data[key] = []


            # load all models for key
            models = getModels(key)
            # # model = gensim.models.doc2vec.Doc2Vec(size=5, min_count=5, iter=55, workers=cores)
            # model = gensim.models.doc2vec.Doc2Vec.load("doc2vec.model")

            # for model in models:

            #     ranks = []
            #     second_ranks = []
            #     for item in range(len(docs[key])):
            #         inferred_vector = model.infer_vector(docs[key][item].words)
            #         sims = model.docvecs.most_similar([inferred_vector], topn=len(model.docvecs))
            #         rank = [item for item, sim in sims].index(item)
            #         ranks.append(rank)    
            #         second_ranks.append(sims[1])

            #     cn_ranks = collections.Counter(ranks)
            #     print cn_ranks
            #     print docs[key]


            #--------
            # check if inferred vectors are close to precalculated ones
            doc_id = np.random.randint(models[0].docvecs.count)  # Pick random doc; re-run cell for more examples
            print('for doc %d...' % doc_id)
            for model in models:
                inferred_docvec = model.infer_vector(docs[key][doc_id].words)
                print('%s:\n %s' % (model, model.docvecs.most_similar([inferred_docvec], topn=3)))
            print '\n\n'

            #--------
            # check if close documents seem more related than distant ones?
            doc_id = np.random.randint(models[0].docvecs.count)  # pick random doc, re-run cell for more examples
            model = random.choice(models)  # and a random model
            sims = model.docvecs.most_similar(doc_id, topn=model.docvecs.count)  # get *all* similar documents
            print(u'TARGET (%d): %s\n' % (doc_id, ' '.join(docs[key][doc_id].words)))
            print(u'SIMILAR/DISSIMILAR DOCS PER MODEL %s:\n' % model)
            for label, index in [('MOST', 0), ('MEDIAN', len(sims)//2), ('LEAST', len(sims) - 1)]:
                print(u'%s %s: %s\n' % (label, sims[index], ' '.join(docs[key][sims[index][0]].words)))
            print '\n\n'

            #--------
            # check if close documents seem more related than distant ones?
            # pick a random word with a suitable number of occurences
            word_models = models[:]
            while True:
                word = random.choice(word_models[0].wv.index2word)
                if word_models[0].wv.vocab[word].count > 10:
                    break
            # or uncomment below line, to just pick a word from the relevant domain:
            #word = 'comedy/drama'
            similars_per_model = [str(model.most_similar(word, topn=20)).replace('), ','),<br>\n') for model in word_models]
            similar_table = ("<table><tr><th>" +
                "</th><th>".join([str(model) for model in word_models]) + 
                "</th></tr><tr><td>" +
                "</td><td>".join(similars_per_model) +
                "</td></tr></table>")
            print("most similar words for '%s' (%d occurences)" % (word, models[0].wv.vocab[word].count))
            HTML(similar_table)
            print '\n\n'


        # else:
        #     print 'skipping {}'.format(key)

    return data


# ------------------------------------------------------

def getFiles(base_path):
    
    files = []
    
    # read in models for each category
    for (dirpath, dirnames, filenames) in os.walk(base_path):
        for f in filenames:
            if f.endswith(".model"):
                temp = os.path.join(dirpath, f)
                files.append(temp)
    return files                

# ------------------------------------------------------

def getModels(key):

    # get base path
    base_path = "/home/janelle/Documents/classes/complexNetworks/TechPaperRec/models"

    # get files list
    files = getFiles(base_path)

    # find files with correct key and open them
    print key
    key_files = [file for file in files if re.search(key, file) != None]

    print key
    print key_files

    # open files and save to model list
    models = []
    for model_name in key_files:
        models.append(Doc2Vec.load(model_name))
    
    return models

# ------------------------------------------------------



# --------------------------------------------------------------
#  main
# --------------------------------------------------------------

def main():

    # open file
    # categories = pickle.load( open("test_clean.p", "r"))
    docsTest = pickle.load( open("test_organize_test.p", "r"))
    doc2tag = pickle.load( open("test_docToTag.p", "r"))

    # print data
    # printCats(categories)

    # test models:
    data = testModels(docsTest, doc2tag)

    # save the data back out
    pickle.dump(data, open("test_testResults.p", "w"))


    print 'done!'


# --------------------------------------------------------------
#  run main
# --------------------------------------------------------------

if __name__ == "__main__":
    startTime = datetime.now()
    main()
    print datetime.now() - startTime   
