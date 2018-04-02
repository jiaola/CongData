
import codecs, sys

file = sys.argv[1]

# remove a few stopwords
lines = list(open(f'corpus/{file}.txt-processed'))
output = codecs.open(f'corpus/{file}-processed.txt', 'w', 'utf-8')
STOPWORDS = ['subparagraph', 'paragraph', 'sec', 'section', 'subsection']
for line in lines:
    id, sponsors, txt, txt_processed = line.strip().split('\t')
    tokens = [ token for token in txt_processed.split() if token not in STOPWORDS]
    output.write(id + '\t' + sponsors + '\t' + txt + '\t' + ' '.join(tokens) + '\n')

