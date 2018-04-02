import sys, spacy, codecs

# bill_type = sys.argv[1]
# year = sys.argv[2]

file = sys.argv[1]

STOPWORDS = ['subparagraph', 'paragraph', 'sec', 'section', 'subsection']

nlp = spacy.load('en')

bills = list(open(f'corpus/{file}.txt'))
docs = [line.split('\t')[2] for line in bills]
processed_docs = []

print(f'processing {len(docs)} documents')
output = codecs.open(f'corpus/{file}-processed.txt', 'w', 'utf-8')
idx = 0
for doc in nlp.pipe(docs):
    # Process document using Spacy NLP pipeline.

    # ents = doc.ents  # Named entities.

    # Keep only words (no numbers, no punctuation).
    # Lemmatize tokens, remove punctuation and remove stopwords.
    doc = [token.lemma_.lower() for token in doc if token.is_alpha and not token.is_stop]

    # Remove common words from a stopword list.
    doc = [token for token in doc if token not in STOPWORDS]

    # Add named entities, but only if they are a compound of more than word.
    # doc.extend([str(entity) for entity in ents if len(entity) > 1])

    # processed_docs.append(doc)
    output.write(bills[idx].rstrip() + "\t" + ' '.join(doc) + "\n")
    idx += 1
output.close()



 