# Usage: python scripts/build_model s-113 [train]

from gensim.models import Phrases, AuthorTopicModel
from pprint import pprint
import os, sys, random

file = sys.argv[1] 
action = sys.argv[2] if len(sys.argv) == 3 else ''

lines = list(open(f'corpus/{file}-processed.txt'))
docs = []
ids = []

sponsor2doc = dict()

for line in lines:
    id, sponsors, txt, txt_processed = line.split('\t')
    for sponsor in sponsors.split(','):
        if not sponsor in sponsor2doc:
            sponsor2doc[sponsor] = []
        sponsor2doc[sponsor].append(id)
    ids.append(id)
    docs.append(txt_processed.split())

# Use an integer ID in sponsor2doc, instead of the IDs extracted from file names. 
# Mapping from ID of document in datast, to an integer ID.
id_dict = dict(zip(ids, range(len(ids))))
# Replace NIPS IDs by integer IDs.
for a, a_doc_ids in sponsor2doc.items():
    for i, doc_id in enumerate(a_doc_ids):
        sponsor2doc[a][i] = id_dict[doc_id]

# Create a dictionary representation of the documents, and filter out frequent and rare words.

from gensim.corpora import Dictionary
dictionary = Dictionary(docs)

# Remove rare and common tokens.
# Filter out words that occur too frequently or too rarely.
max_freq = 0.5
min_wordcount = 20
dictionary.filter_extremes(no_below=min_wordcount, no_above=max_freq)

_ = dictionary[0]  # This sort of "initializes" dictionary.id2token.      

# Vectorize data.

# Bag-of-words representation of the documents.
corpus = [dictionary.doc2bow(doc) for doc in docs]

print('Number of authors: %d' % len(sponsor2doc))
print('Number of unique tokens: %d' % len(dictionary))
print('Number of documents: %d' % len(corpus)) 

def topic_labels(model):
    labels = []
    for topic in model.show_topics(num_topics = 10):
        words = []
        for word, prob in model.show_topic(topic[0]):
            words.append(word)
        labels.append('_'.join(words))
    return labels

def show_sponsor(model, id):
    print('\n%s' % id)
    print('Docs:', model.author2doc[id])
    print('Topics:')
    pprint([(topic_labels(model)[topic[0]], topic[1]) for topic in model[id]])


def get_pairs(nn, names):
    df = pd.DataFrame()
    for x in range(0, nn.shape[0]):
        for y in range(x+1, nn.shape[1]):
            if nn.item(x,y) > 0.0:
                nn.item(x,y)
                df = df.append([[names[x], names[y], nn.item(x,y)]])
    return df


def similarity(vec1, vec2):
    dist = matutils.hellinger(vec1, vec2)
    sim = 1.0 / (1.0 + dist)
    return sim

def get_sims(vec):
    '''Get similarity of vector to all authors.'''
    sims = [similarity(vec, vec2) for vec2 in sponsor_vecs]
    return sims

def get_table(name, top_n=10, smallest_author=1):
    '''
    Get table with similarities, author names, and author sizes.
    Return `top_n` authors as a dataframe.    
    '''
    # Get similarities.
    sims = get_sims(model.get_author_topics(name))
    # Arrange author names, similarities, and author sizes in a list of tuples.
    table = []
    for elem in enumerate(sims):
        author_name = model.id2author[elem[0]]
        sim = elem[1]
        author_size = len(model.author2doc[author_name])
        if author_size >= smallest_author:
            table.append((author_name, sim, author_size))            
    # Make dataframe and retrieve top authors.
    df = pd.DataFrame(table, columns=['Author', 'Score', 'Size'])
    df = df.sort_values('Score', ascending=False)[:top_n]    
    return df   

def get_sponsor_by_term(term):


if action == 'train':
    print("Training...")
    model = AuthorTopicModel(corpus=corpus, num_topics=10, id2word=dictionary.id2token, author2doc=sponsor2doc, chunksize=2000, passes=1, eval_every=0, iterations=1, random_state=1)

    model_list = []
    for i in range(5):
        model = AuthorTopicModel(corpus=corpus, num_topics=10, id2word=dictionary.id2token, author2doc=sponsor2doc, chunksize=2000, passes=100, gamma_threshold=1e-10, eval_every=0, iterations=1, random_state=i)
        top_topics = model.top_topics(corpus)
        tc = sum([t[1] for t in top_topics])
        model_list.append((model, tc))

    model, tc = max(model_list, key=lambda x: x[1])
    print('Topic coherence: %.3e' %tc)

    model.save(f'models/{file}.atmodel')    
    sys.exit 

model = AuthorTopicModel.load(f'models/{file}.atmodel')       
sponsor = random.choice(list(sponsor2doc.keys()))
show_sponsor(model, sponsor)

from gensim.similarities import MatrixSimilarity

# Generate a similarity object for the transformed corpus.
index = MatrixSimilarity(model[list(model.id2author.values())])

from gensim import matutils
import pandas as pd
import numpy as np

sponsor_vecs = [model.get_author_topics(author, 1e-5) for author in model.id2author.values()]
df = pd.DataFrame([matutils.sparse2full(vec, model.num_topics) for vec in sponsor_vecs]).T
similarity_matrix = df.apply(lambda col1: df.apply(lambda col2: similarity(col1, col2)))
nsm = np.asmatrix(similarity_matrix.values)
np.save(f'results/{file}-sim-matrix.npy', nsm)
nsm[nsm < 0.85] = 0
pairs = get_pairs(nsm, list(model.id2author.values()))

np.savetxt(f'results/{file}.csv', pairs, delimiter=',', fmt=['%7s', '%7s', '%1.6e'])

term_vecs = [model.get_term_topics(term, 1e-5) for term in model.id2word.keys()]


