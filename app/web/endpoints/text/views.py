from typing import List, Dict
import numpy
import json

from fastapi import APIRouter, Request, Response, status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends

import nltk
from textblob import TextBlob
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.summarization import summarize

from app.ei.dependancy import generate_text

router = APIRouter()


@router.get("", response_model=Dict[str, List], name="text_analys", summary="Text analysis")
async def find_words(text: str) -> Dict[str, List]:
    """
    NN - существительное, единственное число (Noun, singular)
    NNS - существительное, множественное число (Noun, plural)
    NNP - собственное имя, единственное число (Proper noun, singular)
    NNPS - собственное имя, множественное число (Proper noun, plural)
    VB - глагол, базовая форма (Verb, base form)
    VBD - глагол, прошедшее время (Verb, past tense)
    VBG - глагол, причастие настоящего времени (Verb, gerund/present participle)
    VBN - глагол, причастие прошедшего времени (Verb, past participle)
    VBZ - глагол, третье лицо, настоящее время, единственное число (Verb, third person singular, present tense)
    JJ - прилагательное (Adjective)
    JJR - прилагательное, сравнительная степень (Adjective, comparative)
    JJS - прилагательное, превосходная степень (Adjective, superlative)
    RB - наречие (Adverb)
    RBR - наречие, сравнительная степень (Adverb, comparative)
    RBS - наречие, превосходная степень (Adverb, superlative)
    PRP - местоимение (Pronoun)
    PRP$ - местоимение-притяжательное (Possessive pronoun)
    IN - предлог (Preposition)
    DT - определитель (Determiner)
    CD - числительное (Cardinal number)
    FW - иностранное слово (Foreign word)
    """
    tfidf_vectorizer = TfidfVectorizer()

    # Вычислите TF-IDF для каждого слова
    tfidf_matrix = tfidf_vectorizer.fit_transform(
        [text]
    )
    # Получите список ключевых слов на основе TF-IDF
    feature_names = tfidf_vectorizer.get_feature_names_out()
    sorted_keywords = [feature_names[i] for i in tfidf_matrix.sum(axis=0).argsort()[0, ::-1][:10]]
    words = nltk.word_tokenize(text)
    pos_tags = nltk.pos_tag(words)
    response: Dict[str, List] = {}

    pos: tuple
    for pos in pos_tags:
        try:
            response[pos[1]].append(pos[0])
        except KeyError:
            response[pos[1]] = [pos[0]]

    np_array: numpy.ndarray = numpy.array(sorted_keywords)
    response["popular_sorted"] = np_array.tolist()[0][0]
    return response

@router.get("/short", name='short')
def short_test(text: str):
    try:
        response: str = summarize(text=text)
    except TypeError:
        return "Нужно больше 1-го предложения!++"
    return response


@router.get("/cont", name="cont")
def continue_text(start_text: str, request: Request):
    response: str = generate_text(
        request.app.state.ei, start_text, length=200
    )
    return response

@router.get("/emotion")
def get_emotion_spectrum(text: str):
    sentences: List[str] = re.split(r"[.!?;]", text)
    response: str = ""
    for sentence in sentences:
        blob = TextBlob(sentence)
        sentiment_score = blob.sentiment.polarity

        print(sentiment_score)
        if sentiment_score > 0:
            response += f'<позитив>{sentence}</позитив>'
        elif sentiment_score < 0:
            response += f'<негатив>{sentence}</негатив>'
        else:
            response += f'<нетрально>{sentence}</нетрально>'

    return response
