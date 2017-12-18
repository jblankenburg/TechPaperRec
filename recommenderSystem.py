# recomender system!!!

import itertools
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
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt

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


def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')



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

                # print 'network: {}\n\trecs: {}'.format(network, top)
    print '\n'

    # # save the data?
    # fname = "recommended_" + dataset + ".p"
    # pickle.dump(res, open(fname, "w"))

    fname = "recommended_" + dataset + ".p"
    res = pickle.load(open(fname, "r"))
    for item in res:
        print 'network: {}'.format(item[1])
        count = 0
        for paper in item[2]:
            print '\trecs: {}, {}'.format(doc2tagTrain[paper[1]], tag2catTrain[item[2][count][1]])
            count +=1
        print '\n'

    # save the results?
    print '\nRESULTS FOR TOP RECOMMENDATION:\n'
    resTA_tr = {'automata': [], 'compilers': [], 'CV': [], 'graphics': [], 'ML': [], 'networking': [], 'Parallel': [], 'Robotics': [], 'Security': [], 'SoftwareEngineering': []}
    resAll_tr = {'automata': [], 'compilers': [], 'CV': [], 'graphics': [], 'ML': [], 'networking': [], 'Parallel': [], 'Robotics': [], 'Security': [], 'SoftwareEngineering': []}
    resTA_fa = {'automata': [], 'compilers': [], 'CV': [], 'graphics': [], 'ML': [], 'networking': [], 'Parallel': [], 'Robotics': [], 'Security': [], 'SoftwareEngineering': []}
    resAll_fa = {'automata': [], 'compilers': [], 'CV': [], 'graphics': [], 'ML': [], 'networking': [], 'Parallel': [], 'Robotics': [], 'Security': [], 'SoftwareEngineering': []}
    resCounts = {'allCategories': (resAll_tr,resAll_fa), 'titleAbstract': (resTA_tr, resTA_fa)}
    y_trueTA = []
    y_predTA = []
    y_trueAll = []
    y_predAll = []
    labels = ['automata', 'compilers', 'CV', 'graphics', 'ML', 'networking', 'Parallel', 'Robotics', 'Security', 'SoftwareEngineering', 'N/A']

    for item in res:

        # print 'input: {} network {}:\n\t{}'.format(item[0],item[1],item[2])
        # print 'docid: {} topic: {}\n\tnetwork {}'.format(doc2tag[item[0]], tag2cat[item[0]], item[1])
        # if item[2] == []
            # print 'NO CLOSEST PAPERS FOUND, AS CLOSEST PAPER HAD NO EDGES!'
        # else:
         # print '\t\ttop id:{} sim: {} topic: {}'.format(item[2][0][1], item[2][0][0], tag2catTrain[item[2][0][1]])
        # print '\n'

        # save if correct label
        if item[2] == []:
            resCounts[item[1]][1][tag2cat[item[0]]].append(doc2tag[item[0]])

            if item[1] == 'allCategories':
                y_predAll.append('N/A')
                y_trueAll.append(tag2cat[item[0]])
            else:
                y_predTA.append('N/A')
                y_trueTA.append(tag2cat[item[0]])

        elif tag2cat[item[0]] == tag2catTrain[item[2][0][1]]:
            resCounts[item[1]][0][tag2cat[item[0]]].append(doc2tag[item[0]])
            
            if item[1] == 'allCategories':
                y_predAll.append(tag2catTrain[item[2][0][1]])
                y_trueAll.append(tag2cat[item[0]])
            else:
                y_predTA.append(tag2catTrain[item[2][0][1]])
                y_trueTA.append(tag2cat[item[0]])
                
        # save if incorrect label
        else:
            resCounts[item[1]][1][tag2cat[item[0]]].append(doc2tag[item[0]])


            if item[1] == 'allCategories':
                y_predAll.append(tag2catTrain[item[2][0][1]])
                y_trueAll.append(tag2cat[item[0]])
            else:
                y_predTA.append(tag2catTrain[item[2][0][1]])
                y_trueTA.append(tag2cat[item[0]])

        # print 'docid: {}' .format(doc2tag[item[0]])
        # print 'topic: {}\n'.format( tag2cat[item[0]])
        # print '\tnetwork {}\n'.format(item[1])
        # print item[2]
        # print '\t\ttop id:{}'.format(item[2][0][1])
        # print 'sim: {}'.format( item[2][0][0])
        # print 'topic: {}'.format(tag2catTest[item[2][0][1]])
    print 'papers in allCategories network:\n'
    print(collections.Counter(resCounts[item[1]][0]))
    print 'papers in titleAbstract network:\n'
    print(collections.Counter(resCounts[item[1]][1]))

    # define confusion matrix?
    # for topic in resCounts[item[1]][0]:
    #     for docid in resCounts[item[1]][0][]
    # y_true = [topic for topic ]
    # y_pred = 

    print y_trueTA
    print y_predTA
    ta = confusion_matrix(y_trueTA, y_predTA, labels)
    print ta
    print y_trueAll
    print y_predAll
    allcats = confusion_matrix(y_trueAll, y_predAll, labels)
    print allcats
    # print "test amounts:\n\tautomata: 2    compilers: 4    CV: 3    graphics: 1    ML:4    networking: 3    Parallel: 5    Robotics: 3    Security: 2    Software Engineering: 3"
    print "test amounts: each topic has three."


    # print 'Correctly Labelled: {}\n\tdocis: {}\n'.format(,res[item[0]][0])
    # print 'Wrongly Labelled:   {}\n\tdocids: {}\n\n'.format(res[item[0]][0])


    # plot confusions with matplotlib
    plt.figure()
    plot_confusion_matrix(allcats, labels,
                          normalize=False,
                          title='Top Recommendation - AllCategories Network - Confusion matrix',
                          cmap=plt.cm.Blues)

    # plot confusions with matplotlib
    plt.figure()
    plot_confusion_matrix(ta, labels,
                          normalize=False,
                          title='Top Recommendation - TitleAbstract Network - Confusion matrix',
                          cmap=plt.cm.Blues)

    plt.show()
    print 'done!'


# --------------------------------------------------------------
#  run main
# --------------------------------------------------------------

if __name__ == "__main__":
    startTime = datetime.now()
    main()
    print datetime.now() - startTime   
