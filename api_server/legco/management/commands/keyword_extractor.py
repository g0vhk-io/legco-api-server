# -*- coding: utf-8 -*-
from collections import Counter
import jieba
import jieba.posseg as pseg
import re
import sys
import json
import jieba.analyse
class KeywordExtractor:
    def __init__(self):
        jieba.set_dictionary('dict.txt.big')
        jieba.load_userdict('user_dict.txt')
        jieba.analyse.set_stop_words('stop_words.txt')
        jieba.analyse.set_idf_path('idf.txt')
        self.stop_words = open('stop_words.txt', 'r').read().splitlines()
        jieba.initialize()

    def is_valid(self, x):
        if len(x) == 1:
            return False
        if x in self.stop_words:
            return False
        if x.replace('.','',1).isdigit():
            return False
        return True

    def get_terms(self, content):
        return [x for x in jieba.cut(content, cut_all=False) if self.is_valid(x)]
        
    def get_keywords(self, content):
        content = content.replace(" ","")
        tags = jieba.analyse.extract_tags(content, topK=5, withWeight=True, allowPOS=("nr", "nr", "nz", "nt", "n", "v", "vn"))
        return [x[0] for x in tags if x[1] >= 0.1]
