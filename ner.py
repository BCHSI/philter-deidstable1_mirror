# -*- coding: utf-8 -*-

from nltk.tag.stanford import StanfordNERTagger
from nltk.tokenize import word_tokenize

def formatted_entities(classified_paragraphs_list):
    entities = {'persons': list(), 'organizations': list(), 'locations': list()}

    for classified_paragraph in classified_paragraphs_list:
        for entry in classified_paragraph:
            entry_value = entry[0]
            entry_type = entry[1]

            if entry_type == 'PERSON':
                entities['persons'].append(entry_value)

            elif entry_type == 'ORGANIZATION':
                entities['organizations'].append(entry_value)

            elif entry_type == 'LOCATION':
                entities['locations'].append(entry_value)

    return entities


tagger = StanfordNERTagger('/Users/Shared/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz',
               '/Users/Shared/stanford-ner/stanford-ner.jar',
               encoding='utf-8')


paragraphs = [
            'While in France, Christine Lagarde discussed short-term stimulus efforts in a recent interview with the Wall Street Journal.',
            "Apple Inc. is an American multinational technology company headquartered in Cupertino, California, that designs, develops, and sells consumer electronics, computer software, and online services. Its hardware products include the iPhone smartphone, the iPad tablet computer, the Mac personal computer, the iPod portable media player, the Apple Watch smartwatch, and the Apple TV digital media player. Apple's consumer software includes the OS X and iOS operating systems, the iTunes media player, the Safari web browser, and the iLife and iWork creativity and productivity suites. Its online services include the iTunes Store, the iOS App Store and Mac App Store, and iCloud. Apple was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne on April 1, 1976, to develop and sell personal computers. It was incorporated as Apple Computer, Inc. on January 3, 1977, and was renamed as Apple Inc. on January 9, 2007, to reflect its shifted focus toward consumer electronics. Apple (NASDAQ: AAPL ) joined the Dow Jones Industrial Average on March 19, 2015.",
            "Samuel Patterson Smyth \"Sam\" Pollock, OC, CQ (December 25, 1925 – August 15, 2007) was sports executive who was general manager of the National Hockey League's Montreal Canadiens for 14 years where they won 9 Stanley Cups. Pollock also served as Chairman and CEO of the Toronto Blue Jays baseball club.",
        ]

tokenized_paragraphs = list()

for text in paragraphs:
    tokenized_paragraphs.append(word_tokenize(text))

classified_paragraphs_list = tagger.tag_sents(tokenized_paragraphs)


formatted_result = formatted_entities(classified_paragraphs_list)
print(formatted_result)