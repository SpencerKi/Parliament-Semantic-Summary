# -*- coding: utf-8 -*-
"""
Spencer Y. Ki
2024-11-21
Spying on Parliament, or something
"""
import pandas as pd
import requests as r
import spacy
nlp = spacy.load("en_core_web_lg")

# Dynamic parameters
days = 1
date_range = ""#"date__range=2010-01-01,2010-09-01"

# Static parameters
main = "https://api.openparliament.ca"
pull = "format=json"
with open("UNFCCC.txt", "r") as text:
    unfccc = text.read()
# unfccc = "climate" #test string
base = nlp(unfccc)
results = []

# The actual loop
while days > 0:
    debates = r.get(f"{main}/debates/?{date_range}&{pull}").json()
    for debate in debates["objects"]:
        debate_log = r.get(f"{main}{debate['url']}?{pull}").json()
        speeches = r.get(f"{main}{debate_log['related']['speeches_url']}&{pull}").json()
        while not speeches["pagination"]["next_url"] is None:
            for speech in speeches["objects"]:
                if not speech["procedural"]:
                    speech["similarity"] = nlp(speech["content"]["en"]).similarity(base)
                    results.append(speech)
            speeches = r.get(f"{main}{speeches['pagination']['next_url']}&{pull}").json()
        for speech in speeches["objects"]:
            if not speech["procedural"]:
                speech["similarity"] = nlp(speech["content"]["en"]).similarity(base)
                results.append(speech)
        days -= 1
        if days <= 0:
            break
    debates = r.get(f"{main}{debates['pagination']['next_url']}&{pull}").json()
    
# Export
with pd.ExcelWriter("results.xlsx") as writer:
    pd.DataFrame.from_dict(results)\
        .sort_values("similarity", ascending = False)\
        .to_excel(writer, header = True, index = False)