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

    fname = "recommended_" + dataset + ".p"
    res = pickle.load(open(fname, "r"))

    # print the recommended papers:
    for item in res:
        print 'network: {}'.format(item[1])
        count = 0
        for paper in item[2]:
            print '\trecs: {}, {}'.format(doc2tagTrain[paper[1]], tag2catTrain[item[2][count][1]])
            count +=1
        print '\n'

    # analyze the top results
    print '\nRESULTS FOR TOP RECOMMENDATION:\n'
    resTA_tr = {'automata': [], 'compilers': [], 'CV': [], 'graphics': [], 'ML': [], 'networking': [], 'Parallel': [], 'Robotics': [], 'Security': [], 'SoftwareEngineering': []}
    resAll_tr = {'automata': [], 'compilers': [], 'CV': [], 'graphics': [], 'ML': [], 'networking': [], 'Parallel': [], 'Robotics': [], 'Security': [], 'SoftwareEngineering': []}
    resTA_fa = {'automata': [], 'compilers': [], 'CV': [], 'graphics': [], 'ML': [], 'networking': [], 'Parallel': [], 'Robotics': [], 'Security': [], 'SoftwareEngineering': []}
    resAll_fa = {'automata': [], 'compilers': [], 'CV': [], 'graphics': [], 'ML': [], 'networking': [], 'Parallel': [], 'Robotics': [], 'Security': [], 'SoftwareEngineering': []}
    resCounts = {'allCategories': (resAll_tr,resAll_fa), 'titleAbstract': (resTA_tr, resTA_fa)}
    y_trueTA = [];    y_predTA = [];    y_trueAll = [];    y_predAll = [];
    labels = ['automata', 'compilers', 'CV', 'graphics', 'ML', 'networking', 'Parallel', 'Robotics', 'Security', 'SoftwareEngineering', 'N/A']

    for item in res:

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

    print 'papers in allCategories network:\n'
    print(collections.Counter(resCounts[item[1]][0]))
    print 'papers in titleAbstract network:\n'
    print(collections.Counter(resCounts[item[1]][1]))

    # print y_trueTA; print y_predTA;
    ta = confusion_matrix(y_trueTA, y_predTA, labels);    #print ta;
    # print y_trueAll;    print y_predAll;
    allcats = confusion_matrix(y_trueAll, y_predAll, labels);    #print allcats;
    # print "test amounts: each topic has three."

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
    # plt.show()


#--------------------

    # analyze all of the recommended paper results
    print '\nRESULTS FOR ALL RECOMMENDATIONS:\n'
    resTA_tr = {'automata': [], 'compilers': [], 'CV': [], 'graphics': [], 'ML': [], 'networking': [], 'Parallel': [], 'Robotics': [], 'Security': [], 'SoftwareEngineering': []}
    resAll_tr = {'automata': [], 'compilers': [], 'CV': [], 'graphics': [], 'ML': [], 'networking': [], 'Parallel': [], 'Robotics': [], 'Security': [], 'SoftwareEngineering': []}
    resTA_fa = {'automata': [], 'compilers': [], 'CV': [], 'graphics': [], 'ML': [], 'networking': [], 'Parallel': [], 'Robotics': [], 'Security': [], 'SoftwareEngineering': []}
    resAll_fa = {'automata': [], 'compilers': [], 'CV': [], 'graphics': [], 'ML': [], 'networking': [], 'Parallel': [], 'Robotics': [], 'Security': [], 'SoftwareEngineering': []}
    resCounts = {'allCategories': (resAll_tr,resAll_fa), 'titleAbstract': (resTA_tr, resTA_fa)}
    y_trueTA = [];    y_predTA = [];    y_trueAll = [];    y_predAll = [];
    labels = ['automata', 'compilers', 'CV', 'graphics', 'ML', 'networking', 'Parallel', 'Robotics', 'Security', 'SoftwareEngineering', 'N/A']

    reccomCounts = {'allCategories': [], 'titleAbstract': []}

    for item in res:

        count = 0
        for paper in item[2]:
            # print '\trecs: {}, {}'.format(doc2tagTrain[paper[1]], tag2catTrain[item[2][count][1]])

            # save if correct label
            if item[2] == []:
                resCounts[item[1]][1][tag2cat[item[0]]].append(doc2tag[item[0]])

                if item[1] == 'allCategories':
                    y_predAll.append('N/A')
                    y_trueAll.append(tag2cat[item[0]])
                else:
                    y_predTA.append('N/A')
                    y_trueTA.append(tag2cat[item[0]])

            elif tag2cat[item[0]] == tag2catTrain[item[2][count][1]]:
                resCounts[item[1]][0][tag2cat[item[0]]].append(doc2tag[item[0]])
                
                if item[1] == 'allCategories':
                    y_predAll.append(tag2catTrain[item[2][count][1]])
                    y_trueAll.append(tag2cat[item[0]])
                else:
                    y_predTA.append(tag2catTrain[item[2][count][1]])
                    y_trueTA.append(tag2cat[item[0]])
                    
            # save if incorrect label
            else:
                resCounts[item[1]][1][tag2cat[item[0]]].append(doc2tag[item[0]])


                if item[1] == 'allCategories':
                    y_predAll.append(tag2catTrain[item[2][count][1]])
                    y_trueAll.append(tag2cat[item[0]])
                else:
                    y_predTA.append(tag2catTrain[item[2][count][1]])
                    y_trueTA.append(tag2cat[item[0]])

            count +=1
        reccomCounts[item[1]].append(count)

    print 'papers in allCategories network:'
    print(collections.Counter(resCounts[item[1]][0]))
    print 'papers in titleAbstract network:'
    print(collections.Counter(resCounts[item[1]][1]))

    # print y_trueTA; print y_predTA;
    ta = confusion_matrix(y_trueTA, y_predTA, labels);    #print ta;
    # print y_trueAll;    print y_predAll;
    allcats = confusion_matrix(y_trueAll, y_predAll, labels);    #print allcats;
    # print "test amounts: each topic has three."

    # plot confusions with matplotlib
    plt.figure()
    plot_confusion_matrix(allcats, labels,
                          normalize=False,
                          title='All Recommendations - AllCategories Network - Confusion matrix',
                          cmap=plt.cm.Blues)

    # plot confusions with matplotlib
    plt.figure()
    plot_confusion_matrix(ta, labels,
                          normalize=False,
                          title='All Recommendations - TitleAbstract Network - Confusion matrix',
                          cmap=plt.cm.Blues)



    print 'AllCats recommended {} papers total'.format(sum(ta))
    print 'TA recommended {} papers total'.format(sum(ta))

    print 'Papers with a given number of recommendations returned:'
    print(collections.Counter(reccomCounts[item[1]]))



    plt.show()







    print 'done!'




# --------------------------------------------------------------
#  run main
# --------------------------------------------------------------

if __name__ == "__main__":
    startTime = datetime.now()
    main()
    print datetime.now() - startTime   
