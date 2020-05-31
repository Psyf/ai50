import nltk
nltk.download('stopwords')

import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    dir_content = {}
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    for f_name in files: 
        with open(os.path.join(directory, f_name), 'r') as f_handle: 
            dir_content[f_name] = f_handle.read()

    return dir_content

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    first_pass = [word for word in nltk.tokenize.word_tokenize(document.lower()) if word not in nltk.corpus.stopwords.words("english")] 
    second_pass = []

    for word in first_pass:
        valid = True 
        for char in word: 
            if char in string.punctuation: 
                valid = False
                break
        if valid: 
            second_pass.append(word)

    return second_pass

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    total_docs = len(documents)
    result = {}

    for doc in documents: 
        for word in documents[doc]: 
            if word not in result: 
                counter = 1
                for other_doc in documents: 
                    if other_doc == doc:
                        continue 
                    elif word in documents[other_doc]: 
                            counter += 1
                result[word] = math.log(total_docs/counter)

    return result

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tuple_list = []

    for f_name in files: 
        score = 0
        for word in query: 
            count = files[f_name].count(word)
            tf_idf = idfs[word] * count 
            score += tf_idf

        tuple_list.append((-score, f_name))

    tuple_list = sorted(tuple_list)
    return [item[1] for item in tuple_list[:n]]

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    result_list = []
    for key, sentence in sentences.items():
        score = 0
        q_density = 0
        for word in query: 
            if word in sentence: 
                score += idfs[word]
                q_density += 1
        result_list.append((score, q_density/len(sentence), key))

    result_list.sort(reverse=True)
    return [item[2] for item in result_list[:n]]

if __name__ == "__main__":
    main()
