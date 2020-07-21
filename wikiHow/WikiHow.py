"""
    Wikihow class to download and preprocess Wikihow dataset
"""

import os
from bs4 import BeautifulSoup
import requests
import json
import re
import spacy
import tqdm

class WikiHow:
    def __init__(self, dataset_folder):
        self.normalization = [("it's", "it is"), ("doesn't", "does not"), ("don't", "do not")]

        self.stop_words = ['a', 'an', 'this', 'that', 'the', 'and', 'or',
            'with', 'to', 'on', 'in', 'into', 'at', 'until', 'is', 'are',
            'some' 'any', 'many']
        self.object_pronouns = ['it', 'them']
        self.folder=dataset_folder


        if os.path.exists(self.folder):
            self.files_list = os.listdir(os.path.abspath(self.folder))

        self.nlp = spacy.load('en_core_web_sm')


    def __len__(self):
        return len(self.files_list)


    def download(self):
        # Get list of url categories
        print("Downloading Wikihow dataset ...")

        categories_url_list = []
        with open('./wikihow/categories_list', 'r') as file:
            line = file.readline()
            while line:
                categories_url_list.append(line)
                line = file.readline()

        # Create dataset folder
        if not os.path.exists(self.folder):
            try:
                os.makedirs(self.folder)
            except OSError:
                print("Error creating dataset directory {}".format(self.folder))

        # Get url links by parsing categories url
        url_list = []

        for category_url in categories_url_list[:2]:
            req = requests.get(category_url)
            soup = BeautifulSoup(req.content, 'html.parser')

            div_categories = soup.findAll('div', {'class': 'responsive_thumb'})

            for div in div_categories:
                link = div.find('a')
                url_list.append(link.get('href'))

        # Download url content
        for url in url_list[:2]:
            req = requests.get(url)
            soup = BeautifulSoup(req.content, 'html.parser')

            scripts = soup.findAll('script', {'type': 'application/ld+json'})
            js = None
            steps = None

            for script in scripts:
                js = json.loads(script.string)

                if 'headline' in js:
                    headline = js['headline']

                if 'step' in js:
                    steps = js['step']
                    break

            if steps == None:
                print("Ignoring file {} (wrong format) ...".format(file_name))
                continue

            # Write content to file
            file_name = url.split('/')[-1]

            with open(os.path.join(os.path.abspath(self.folder), file_name), 'w') as file:
                file.write("TITLE: {} ({})\n".format(str.upper(headline), url))
                idx = 1

                for step in steps:
                    if step['@type'] == 'HowToStep':
                        file.write("\nSTEP {}. {}\n".format(idx, step['text']))
                    elif step['@type'] == 'HowToSection':
                        file.write("\nSECTION: {}\n".format(str.upper(step['name'])))

                        for item in step['itemListElement']:
                            if item['@type'] == 'HowToStep':
                                file.write("\nSTEP {}. {}\n".format(idx, item['text']))
                                idx += 1
                    idx += 1


    def get_files_list(self):
        files = []
        for file in self.files_list:
            files.append(os.path.join(os.path.abspath(self.folder), file))
        return files


    def process_instance(self, text):
        lines = text.split('\n')
        lines = [l for l in lines if len(l) > 0]

        entries = []
        for line in lines:

            if re.match('^STEP.*', line):
                text = line.lower().replace(',', '').split('.')[1].rstrip().lstrip()

                # Perform normalization
                for entry in self.normalization:
                    text = text.replace(entry[0], entry[1])

                print("\nText: {}".format(text))

                # Find object pronouns and replace with previous seen noun in sentence
                text = self.nlp(text)
                tokens = [(e, e.dep_) for e in text]

                for idx, token in enumerate(tokens):
                    if str(token[0]) in self.object_pronouns:
                        idx_noun = idx - 1
                        while idx_noun > 0:
                            if str(tokens[idx_noun][1]) in ['dobj', 'pobj']:
                                last_noun = str(tokens[idx_noun][0])
                                text = str(text[:idx]) + " the " + last_noun + " " + str(text[idx + 1:])
                                break
                            idx_noun -= 1

                # If sentence includes 'and' conjunction, separate into distinct steps
                and_separator = str(text).split(' and ')
                if len(and_separator) > 1:
                    for idx, entry in enumerate(and_separator):
                        # Check if there are verbs available in sub-sentence
                        text = self.nlp(entry)
                        tokens = [(e, e.dep_) for e in text]
                        if str(tokens[0][1]) != 'ROOT':
                            # Retrieve verb from previous sentence
                            if idx > 0:
                                tokens_verb = [e for e in self.nlp(and_separator[idx - 1]) if e.dep_ == 'ROOT'][0]
                                entry = str(tokens_verb) + " " + str(entry)

                        print(entry)
                        entries.append(entry.rstrip().lstrip())
                else:
                    print(text)
                    entries.append(text)
        return entries


    def get_instance(self, file_idx):
        with open(os.path.join(os.path.abspath(self.folder), self.files_list[file_idx]), 'r') as file:
            return (self.files_list[file_idx], file.read())


    def get_statistics(self):
        print("Generating dataset statistics information ...")
        total_sentences = 0
        total_words = 0
        # Keywords are verbs and nouns
        key_words = []

        for idx, file in enumerate(self.files_list):
            text = open(os.path.join(os.path.abspath(self.folder), file), 'r').read()
            sentences = self.process_instance(text)
            total_sentences += len(sentences)

            for sentence in sentences:
                doc = self.nlp(sentence)
                sentence_tokens = [t for t in doc]
                total_words += len(sentence_tokens)
                sentence_tags = [(str(t), t.pos_) for t in doc]
                key_words.append([v for v in doc if str(v) not in self.stop_words])
            print(idx)

        flatten = lambda l: [str(item) for sublist in l for item in sublist]
        key_words = flatten(key_words)

        with open(os.path.join('./', 'wikihow_dataset_statistics.txt'), 'w') as f:
            f.write("\nTotal of instances: {}".format(len(self.files_list)))
            f.write("\nTotal of sentences: {} - mean: {:.4f}".format(total_sentences, total_sentences / len(self.files_list)))
            f.write("\nTotal of words: {} - mean per text: {:.4f} - per sentence: {}".format(total_words, total_words / len(self.files_list), total_words / total_sentences))
            f.write("\nTotal of key words: {}".format(len(key_words)))

            f.write("\n\n")
            import pandas as pd
            df = pd.DataFrame(key_words)[0].value_counts().to_string()
            f.write(df)
