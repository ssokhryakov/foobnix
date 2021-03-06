#-*- coding: utf-8 -*-
'''
Created on 20 February 2010

@author: Dmitry Kogura (zavlab1)
'''

from __future__ import with_statement
import os
from foobnix.util.singleton import Singleton
from foobnix.fc.fc_helper import CONFIG_DIR, FCStates

CACHE_FILE = os.path.join(CONFIG_DIR, "foobnix_cache.pkl")
COVERS_DIR = os.path.join(CONFIG_DIR, 'covers','')
LYRICS_DIR = os.path.join(CONFIG_DIR, 'lirics','')

CACHE_COVERS_FILE = os.path.join(COVERS_DIR, 'covers_cache')
CACHE_ALBUM_FILE = os.path.join(CONFIG_DIR, 'albums_cache')
CACHE_RADIO_FILE = os.path.join(CONFIG_DIR, 'radio_cache')

"""Foobnix cache"""
class FCache:
    __metaclass__ = Singleton
    def __init__(self):
        self.covers = {}
        self.album_titles = {}
        
        """music library"""
        self.tab_names = [_("Empty tab"), ]
        self.last_music_path = None
        self.music_paths = [[], ]
        self.cache_music_tree_beans = [[], ]
        
        self.cache_virtual_tree_beans = []
        self.cache_radio_tree_beans = []
        self.cache_pl_tab_contents = []
        self.tab_pl_names = [_("Empty tab"), ]
        
        self.load()
        
    def save(self):
        FCStates().save(self, CACHE_FILE)
    
    def load(self):
        FCStates().load(self, CACHE_FILE)

    def on_load(self):
        if os.path.isfile(CACHE_COVERS_FILE):
            '''reading cover cache file in dictionary'''
            with file(os.path.join(COVERS_DIR, 'covers_cache'),'r') as cov_conf:
                for line in cov_conf:
                    if line.startswith('#') and not FCache().covers.has_key(line[1:-1]):
                        FCache().covers[line[1:-1]] = cov_conf.next()[:-1].split(", ")
                   
        if os.path.isfile(CACHE_ALBUM_FILE):
            '''reading cover cache file in dictionary'''
            with file(os.path.join(CONFIG_DIR, 'albums_cache'), 'r') as albums_cache:
                for line in albums_cache:
                    if line.startswith('#') and not FCache().album_titles.has_key(line[1:-1]):
                        FCache().album_titles[line[1:-1]] = albums_cache.next()[:-1]
         
    def on_quit(self):
        if not os.path.isdir(COVERS_DIR):
            os.mkdir(COVERS_DIR)
            
        with file(CACHE_COVERS_FILE, 'w') as f:
            for key, value in zip(FCache().covers.keys(), FCache().covers.values()):
                f.write('#' + key + '\n' + ','.join(value) + '\n')
                
        with file(CACHE_ALBUM_FILE, 'w') as f:
            for key, value in zip(FCache().album_titles.keys(), FCache().album_titles.values()):
                f.write('#' + key + '\n' + value + '\n')