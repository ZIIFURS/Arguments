from pyspark.sql import SparkSession
from pyspark.sql.functions import array_contains
from pyspark.ml.feature import Tokenizer
from pyspark.ml.feature import StopWordsRemover
from pyspark.ml.feature import CountVectorizer
from pyspark.ml.feature import IDF
from pyspark.ml.feature import Word2Vec
import numpy as np
import Cython

def spark_text(word):
    spark = SparkSession \
        .builder \
        .appName("SimpleApplication") \
        .getOrCreate()

    # Построчная загрузка файла в RDD
    input_file = spark.sparkContext.textFile('/home/ubuntu/spark_app/Samples/1.txt')

    print(input_file.collect())
    prepared = input_file.map(lambda x: ([x]))
    df = prepared.toDF()
    prepared_df = df.selectExpr('_1 as text')

    # Разбить на токены
    tokenizer = Tokenizer(inputCol='text', outputCol='words')
    words = tokenizer.transform(prepared_df)

    # Удалить стоп-слова
    stop_words = StopWordsRemover.loadDefaultStopWords('russian')
    remover = StopWordsRemover(inputCol='words', outputCol='filtered', stopWords=stop_words)
    filtered = remover.transform(words)

    # Вывести стоп-слова для русского языка
    print(stop_words)

    # Вывести таблицу filtered
    filtered.show()

    # Вывести столбец таблицы words с токенами до удаления стоп-слов
    words.select('words').show(truncate=False, vertical=True)

    # Вывести столбец "filtered" таблицы filtered с токенами после удаления стоп-слов
    filtered.select('filtered').show(truncate=False, vertical=True)

    # Посчитать значения TF
    vectorizer = CountVectorizer(inputCol='filtered', outputCol='raw_features').fit(filtered)
    featurized_data = vectorizer.transform(filtered)
    featurized_data.cache()
    vocabulary = vectorizer.vocabulary

    # Вывести таблицу со значениями частоты встречаемости термов.
    featurized_data.show()

    # Вывести столбец "raw_features" таблицы featurized_data
    featurized_data.select('raw_features').show(truncate=False, vertical=True)

    # Вывести список термов в словаре
    print(vocabulary)

    # Посчитать значения DF
    idf = IDF(inputCol='raw_features', outputCol='features')
    idf_model = idf.fit(featurized_data)
    rescaled_data = idf_model.transform(featurized_data)

    # Вывести таблицу rescaled_data
    rescaled_data.show()

    # Вывести столбец "features" таблицы featurized_data
    rescaled_data.select('features').show(truncate=False, vertical=True)

    # Построить модель Word2Vec
    word2Vec = Word2Vec(vectorSize=3, minCount=0, inputCol='words', outputCol='result')
    model = word2Vec.fit(words)
    w2v_df = model.transform(words)
    w2v_df.show()

    # input_word = input("Введите слово, для которого хотите найти синонимы и ассоциированные слова: ")

    synonyms = model.findSynonyms(word, 5)

    print(f"Контекстные синонимы для '{word}':")
    synonyms.show()

    associated_words = w2v_df.filter(array_contains(w2v_df['words'], word)).select('words')
    print(f"Слова, ассоциированные с '{word}' в тексте :")
    associated_words.show()

    # model_output = f"Модель Word2Vec:\n{model.getVectors().collect()}\n"
    # synonyms_output = f"Контекстные синонимы для '{word}:\n{model.findSynonyms(word, 5).collect()}\n"
    # associated_output = f"Слова, ассоциированные с '{word}' в тексте:\n{w2v_df.filter(array_contains(w2v_df['filtered'], word)).select('filtered').collect()}\n"


    # return model_output, synonyms_output, associated_output