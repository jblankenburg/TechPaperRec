# recomender system!!!

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
import copy
import sys
from scipy import spatial

# os.system("taskset -p 0xff %d" % os.getpid())

THRESH = 5

# --------------------------------------------------------------

# Define function for getting list of all files to parse
def getFiles(base_path, ext):
    files  =[]
    for (dirpath, dirnames, filenames) in os.walk(base_path):
        for f in filenames:
            if f.endswith(ext):
                temp = os.path.join(dirpath, f)
                files.append(temp)
                
    return files

# ------------------------------------------------------

def getModels(key):

    # get base path
    base_path = "/home/janelle/Documents/classes/complexNetworks/TechPaperRec/models"

    # get files list
    files = getFiles(base_path, '.model')

    # find files with correct key and open them
    key_files = [file for file in files if re.search(key, file) != None]

    # open files and save to model list
    models = []
    for model_name in key_files:
        models.append(Doc2Vec.load(model_name))
    
    return models


# --------------------------------------------------------------

def getMostSim(doc, indx):

    # iterate through keys and 
    most_similar = {}
    ranksAll = []
    ranksTA = []
    for key in doc:

        # load all models for key
        models = getModels(key)
        # for now, just use first model!!!!
        model = models[0]

        # get inferred vector and the most_similar doc?
        inferred = model.infer_vector(doc[key].words)
        # print key
        # print('{}'.format(model.docvecs.most_similar([inferred], topn=5)))
        sims = model.docvecs.most_similar([inferred], topn=5)

        # get most_similar for title and abstract only
        if key == 'title' or key == 'abstract':
            for docid, sim in sims:
                ranksTA.append(docid)

        # get most_similar for all cats
        for docid, sim in sims:
            ranksAll.append(docid)
            
        
    most_similar['allCategories'] = collections.Counter(ranksAll).most_common(1)[0][0]
    most_similar['titleAbstract'] = collections.Counter(ranksTA).most_common(1)[0][0]

    return most_similar

# --------------------------------------------------------------

def reorder(docs, doc2tag):

    docs_rot = {}
    for indx in doc2tag:
        docs_rot[indx] = {'title': [], 'abstract': [], 'introduction': [], 'related work': [], 'methodology': [], 'discussion': [], 'conclusion': [] }

    for key in docs:
        for indx in doc2tag:
            # print docs[key][indx].tags

            print key 
            print indx

            docs_rot[indx][key] = docs[key][indx-100]

    #  verify manually this was done right by printing
    # for indx in docs_rot:
    #     for key in docs_rot[indx]:
            # print docs_rot[indx][key].tags

    return docs_rot


# --------------------------------------------------------------


def gatherFriends(most_similar, edges):
    # TODO: will break if things don't have any children sorta thing

    candidates = []

    # go through edges and get all edges from most_similar
    for edge in edges:
        if edge[0] == most_similar:
            if not edge[1] in candidates: 
                candidates.append(edge[1])

    print 'initial candidates list:'
    print candidates

    #  get more candidates if not > THRESH
    if len(candidates) < THRESH:
        children = copy.deepcopy(candidates)
        while( len(candidates) < THRESH):
            print 'ADDING MORE CANDIDATES!'
            new_children = []
            for child in children:
                for edge in edges:
                    if edge[0] == child:
                        if not edge[1] in candidates:
                            candidates.append(edge[1])
                            new_children.append(edge[1])
            if set(children) == set(new_children):
                print 'WARNING: Not enough connected edges in network. Only generated {} candidates.'.format(len(new_children)) 
                return candidates
            print candidates
            children = copy.deepcopy(new_children)

    return candidates

# --------------------------------------------------------------

def rankCandidates(doc, indx, candidates, network):

    ranked = []
    for candidate in candidates:

        similarity = calcSimilarities(doc, indx, candidate, network)
        ranked = updateRanks(candidate, similarity, ranked)

    return ranked

# ------------------------------------------------------

def calcSimilarities(doc, indx, candidate, network):


    #  get similarity for each doc for each category
    similarities = {'title': 0, 'abstract': 0, 'introduction': 0, 'related work': 0, 'methodology': 0, 'discussion': 0, 'conclusion': 0}
    for key in doc:

        # load all models for key
        models = getModels(key)
        # for now, just use first model!!!!
        model = models[0]

        # print key
        # similarities[key] = (model.docvecs.similarity(indx,candidate))
        inferred = model.infer_vector(doc[key].words)
        # print inferred
        learned = model.docvecs[candidate]
        # print learned
        similarities[key] = 1 - spatial.distance.cosine(inferred, learned)
        print '\t{}'.format(similarities[key])




    if network == 'titleAbstract':
        return ((similarities['title'] + similarities['abstract']) / 2)
    else:
        similarity = 0
        for key in similarities:
            similarity += similarities[key]
        return similarity/7

# ------------------------------------------------------

def updateRanks(candidate, similarity, ranked):

    if ranked == []:
        return [(similarity, candidate)]

    # place candidate in correct spot based on similarity
    indx = 0
    for sim, cand in ranked:
        if similarity > sim:
            if indx == 0:
                return [(similarity, candidate)] + ranked
            else:
                ranked = ranked[:indx] + [(similarity, candidate)] + ranked[indx:] # TODO: Check this logic!!!
                return ranked
        indx += 1

    return ranked + [(similarity, candidate)]

# ------------------------------------------------------

def reorgCat2Tag(cat2tag):

    new_cat = {}
    for cat in cat2tag:
        for tag in cat2tag[cat]:
            new_cat[tag] = cat

    return new_cat

# --------------------------------------------------------------


# --------------------------------------------------------------
#  main
# --------------------------------------------------------------

def main():


    # NOTE: dataset should be set as "training" or "test"
    dataset = sys.argv[1]

     # open file
    fname = "edgeLists_" + "train" + ".p"
    edgeLists = pickle.load(open(fname, "r"))
    fname = "reorganized_docs_" + dataset + ".p"
    docs = pickle.load( open(fname, "r"))
    fname = "reorganized_doc2tag_" + dataset + ".p"
    doc2tag = pickle.load( open(fname, "r"))
    fname = "reorganized_doc2tag_" + "train" + ".p"
    doc2tagTrain = pickle.load( open(fname, "r"))
    fname = "reorganized_cat2tag_" + dataset + ".p"
    cat2tag = pickle.load( open(fname, "r"))
    fname = "reorganized_cat2tag_" + "train" + ".p"
    cat2tagTrain = pickle.load( open(fname, "r"))

    # reorg for printing below
    tag2cat = reorgCat2Tag(cat2tag)
    tag2catTrain = reorgCat2Tag(cat2tagTrain)

    # get set of nput papers)
    fname = '/home/janelle/Documents/classes/complexNetworks/paper/' + dataset
    files = getFiles(fname, '.tex')

    #  pre-process paper (assume this already happened for now, if time fix later....)
    #     for now just need to reorder the data, which will still have to happend later too...
    docs = reorder(docs, doc2tag)

    # for each ppaer
    res = []
    for indx in docs:

        print 'starting paper: {}'.format(indx)

        # get most_similar paper for both networks
        most_similar = getMostSim(docs[indx], indx)


        # for each network:
        for network in most_similar:

            # if network == 'titleAbstract':

                # gather friends of paper until have m >= n friends
                candidates = gatherFriends(most_similar[network], edgeLists[network])

                # rank papers by highest similarity to input
                ranked = rankCandidates(docs[indx], indx, candidates, network)

                # return top n papers
                top = ranked[:THRESH]
                # print 'input: {} network {}:\n\t{}'.format(indx,network,top)
                res.append((indx,network,top))


    for item in res:

        print item

        # print 'input: {} network {}:\n\t{}'.format(item[0],item[1],item[2])
        print 'docid: {} topic: {}\n\tnetwork {}'.format(doc2tag[item[0]], tag2cat[item[0]], item[1])
        if item[2] == []:
            print 'NO CLOSEST PAPERS FOUND, AS CLOSEST PAPER HAD NO EDGES!'
        else:
         print '\t\ttop id:{} sim: {} topic: {}'.format(item[2][0][1], item[2][0][0], tag2catTrain[item[2][0][1]])
        print '\n'

        # print 'docid: {}' .format(doc2tag[item[0]])
        # print 'topic: {}\n'.format( tag2cat[item[0]])
        # print '\tnetwork {}\n'.format(item[1])
        # print item[2]
        # print '\t\ttop id:{}'.format(item[2][0][1])
        # print 'sim: {}'.format( item[2][0][0])
        # print 'topic: {}'.format(tag2catTest[item[2][0][1]])



    print 'done!'


# --------------------------------------------------------------
#  run main
# --------------------------------------------------------------

if __name__ == "__main__":
    startTime = datetime.now()
    main()
    print datetime.now() - startTime   
