# generate the graphs for training set!!!

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
import sys


# os.system("taskset -p 0xff %d" % os.getpid())


# --------------------------------------------------------------


def buildEdgeLists(docs, doc2tag):

    # iterate through pairs of papers and if siilarity above threshold, then create edge between papers.
    numPapers = len(doc2tag)

    edgeLists = {'allCategories': [], 'titleAbstract': []} # TODO: when keywords work, need to add this as third network

    startTimeSim = datetime.now()
    print 'starting to calc similarities: {}'.format(startTimeSim)

    count = 0
    for i in doc2tag:
        count += 1

    for i in doc2tag:

        print 'searching edges in doc {}'.format(i)

        # get most similar papers
        similarities = mostSimilar(docs, i, count)

        # if similarity above threshold, add edge to network
        edgeLists = findEdges(edgeLists, similarities, i, count)


    print 'similarities calced in {}\n'.format(datetime.now() - startTimeSim)

    return edgeLists


# ------------------------------------------------------

def findEdges(edgeLists, similarities, i, count):

    # reformat similarities by docid
    simsAll = {}
    simsTA = {}
    for key in similarities:
        # iterate through the list of similar docs and keep those above threshold
        for docid, sim in similarities[key]:
            if docid in simsAll.keys():
                simsAll[docid].append(sim)
            else:
                simsAll[docid] = [sim]
        if key == 'title' or key == 'introduction':
            if docid in simsTA.keys():
                simsTA[docid].append(sim)
            else:
                simsTA[docid] = [sim]

    threshold = 0.75

    # get avg of sims
    for docid in simsAll:
        avg = np.mean(simsAll[docid])
        print '\t\t {}, {}\tavg = {}'.format(i, docid, avg)
        if avg > threshold:
            edgeLists['allCategories'].append((i,docid,avg))

    # get avg of sims
    for docid in simsTA:
        avg = np.mean(simsTA[docid])
        if avg > threshold:
            edgeLists['titleAbstract'].append((i,docid,avg))

    return edgeLists

# ------------------------------------------------------

def mostSimilar(docs, i, count):

    #  get similarity for each doc for each category
    similarities = {'title': 0, 'abstract': 0, 'introduction': 0, 'related work': 0, 'methodology': 0, 'discussion': 0, 'conclusion': 0}
    for key in docs:

        # load all models for key
        models = getModels(key)
        # for now, just use first model!!!!
        model = models[0]

        # get inferred vector and the most_similar doc?
        inferred = model.infer_vector(docs[key][i].words)
        # print key
        # print('{}'.format(model.docvecs.most_similar([inferred], topn=5)))
        similarities[key] = model.docvecs.most_similar([inferred], topn=count)

        # print '\tnum sim docs to search: {}'.format(len(similarities[key]))

    return similarities

# ------------------------------------------------------

def getModels(key):

    # get base path
    base_path = "/home/janelle/Documents/classes/complexNetworks/TechPaperRec/models"

    # get files list
    files = getFiles(base_path)

    # find files with correct key and open them
    key_files = [file for file in files if re.search(key, file) != None]

    # open files and save to model list
    models = []
    for model_name in key_files:
        models.append(Doc2Vec.load(model_name))
    
    return models

# --------------------------------------------------------------

# Define function for getting list of all files to parse
def getFiles(base_path):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(base_path):
        for f in filenames:
            if f.endswith(".model"):
                temp = os.path.join(dirpath, f)
                files.append(temp)
                
    return files

# ------------------------------------------------------

def reorgCat2Tag(cat2tag):

    new_cat = {}
    for cat in cat2tag:
        for tag in cat2tag[cat]:
            new_cat[tag] = cat

    return new_cat

# ------------------------------------------------------


def generateNetworks(edgeLists, doc2tag, cat2tag):

    # reverse to look up cat by tag
    tag2cat = reorgCat2Tag(cat2tag)

    # go through edgeLists and generate a .gdf file for each network from lists
    for key in edgeLists:
        print key

        file_name = 'gdf/network_{}.gdf'.format(key)
        with open(file_name, 'w') as fin:

            #  write the nodes
            fin.write('nodedef>name VARCHAR,label VARCHAR, category VARCHAR\n')
            for tag in doc2tag:
                fin.write('{}, {},{}\n'.format(tag, doc2tag[tag], tag2cat[tag]))
               #TODO: add in the topic so that I can sort the things by them!!!! will need 
                # to save off topc data like with doc2tag sorta thing

            # write the edges
            fin.write('edgedef>node1 VARCHAR,node2 VARCHAR,weight DOUBLE\n')
            for edge in edgeLists[key]:
                fin.write('{}, {}, {}\n'.format(edge[0], edge[1], edge[2]))



# --------------------------------------------------------------
#  main
# --------------------------------------------------------------

def main():


    # NOTE: dataset should be set as "training" or "test"
    dataset = sys.argv[1]

    # open file
    fname = "reorganized_docs_" + dataset + ".p"
    docs = pickle.load( open(fname, "r"))
    fname = "reorganized_doc2tag_" + dataset + ".p"
    doc2tag = pickle.load( open(fname, "r"))
    fname = "reorganized_cat2tag_" + dataset + ".p"
    cat2tag = pickle.load( open(fname, "r"))

    # print data
    # printCats(categories)

    # test models:
    edgeLists = buildEdgeLists(docs, doc2tag)

    # TODO: So don't have to rerun this, save our edge lists so next time can just read this in so that I can write the next file to generate the gdf files.
    fname = "edgeLists_" + dataset + ".p"
    pickle.dump(edgeLists, open(fname, "w"))
    # edgeLists = pickle.load(open("test_edgeLists.p", "r"))

    # print edgeLists

    # save the data back out
    # pickle.dump(data, open("test_testResults.p", "w"))
    generateNetworks(edgeLists, doc2tag, cat2tag)

    print 'done!'


# --------------------------------------------------------------
#  run main
# --------------------------------------------------------------

if __name__ == "__main__":
    startTime = datetime.now()
    main()
    print datetime.now() - startTime   
