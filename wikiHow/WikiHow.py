"""
    Wikihow class to download and preprocess Wikihow dataset
"""

import os
from bs4 import BeautifulSoup
import requests
import json
import re
import spacy

class WikiHow:
    def __init__(self, dataset_folder):
        self.folder=dataset_folder

        if os.path.exists(self.folder):
            self.files_list = os.listdir(os.path.abspath(self.folder))


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
                entries.append(line.lower().replace(',', '').split('.')[1].rstrip().lstrip())

        return entries


    def get_instance(self, file_idx):
        with open(os.path.join(os.path.abspath(self.folder), self.files_list[file_idx]), 'r') as file:
            return (self.files_list[file_idx], file.read())


    def get_statistics(self):
        print("Generating dataset statistics information ...")
        total_sentences = 0
        total_words = 0
        verbs = []
        spacy_en = spacy.load('en_core_web_sm')

        for idx, file in enumerate(self.files_list):
            text = open(os.path.join(os.path.abspath(self.folder), file), 'r').read()
            sentences = self.process_instance(text)
            total_sentences += len(sentences)

            for sentence in sentences:
                doc = spacy_en(sentence)
                sentence_tokens = [t for t in doc]
                total_words += len(sentence_tokens)
                sentence_tags = [(str(t), t.pos_) for t in doc]
                verbs.append([v for v in doc if v.pos_ == 'VERB'])

            print(idx)


        flatten = lambda l: [str(item) for sublist in l for item in sublist]
        verbs = flatten(verbs)

        print()
        print("Total of instances: {}".format(len(self.files_list)))
        print("Total of sentences: {} - mean: {:.4f}".format(total_sentences, total_sentences / len(self.files_list)))
        print("Total of words: {} - mean per text: {:.4f} - per sentence: {}".format(total_words, total_words / len(self.files_list), total_words / total_sentences))
        print("Total of verbs: {}".format(len(verbs)))

        import pandas as pd
        df = pd.DataFrame(verbs)[0].value_counts().to_csv('dataset_statistics2.csv')
