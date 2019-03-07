%pyspark
wordsDF = sqlContext.createDataFrame([('cat',), ('elephant',), ('rat',), ('rat',), ('cat', )], ['word'])
wordsDF.show()
print type(wordsDF)
wordsDF.printSchema()

//======================================================================
%pyspark
# TODO: Replace <FILL IN> with appropriate code
# Using DataFrame functions to add an 's'
from pyspark.sql.functions import lit, concat

pluralDF = wordsDF.select(concat(wordsDF.word,lit('s')).alias('word'))
pluralDF.show()

//======================================================================
%pyspark
# TODO: Replace <FILL IN> with appropriate code
from pyspark.sql.functions import length
pluralLengthsDF = pluralDF.select(length(pluralDF.word))
pluralLengthsDF.show()

//======================================================================
%pyspark
# TODO: Replace <FILL IN> with appropriate code
wordCountsDF = (wordsDF
                .groupBy(wordsDF.word).count())
wordCountsDF.show()

//======================================================================
%pyspark
# TODO: Replace <FILL IN> with appropriate code
uniqueWordsCount = wordCountsDF.select('word').count()
print uniqueWordsCount

//======================================================================
%pyspark
# TODO: Replace <FILL IN> with appropriate code
averageCount = (wordCountsDF.
                groupBy().mean('count').collect()[0][0]
                )

print averageCount


//======================================================================
%pyspark
# TODO: Replace <FILL IN> with appropriate code
def wordCount(wordListDF):
    """Creates a DataFrame with word counts.

    Args:
        wordListDF (DataFrame of str): A DataFrame consisting of one string column called 'word'.

    Returns:
        DataFrame of (str, int): A DataFrame containing 'word' and 'count' columns.
    """
    return wordListDF.groupBy('word').count()

wordCount(wordsDF).show()


//======================================================================
%pyspark
# TODO: Replace <FILL IN> with appropriate code
from pyspark.sql.functions import regexp_replace, trim, col, lower
def removePunctuation(column):
    """Removes punctuation, changes to lower case, and strips leading and trailing spaces.

    Note:
        Only spaces, letters, and numbers should be retained.  Other characters should should be
        eliminated (e.g. it's becomes its).  Leading and trailing spaces should be removed after
        punctuation is removed.

    Args:
        column (Column): A Column containing a sentence.

    Returns:
        Column: A Column named 'sentence' with clean-up operations applied.
    """
    return trim(lower(regexp_replace(column, '[^A-Za-z0-9 ]', ''))).alias('sentence')

sentenceDF = sqlContext.createDataFrame([('Hi, you!',),
                                         (' No under_score!',),
                                         (' *      Remove punctuation then spaces  * ',)], ['sentence'])
sentenceDF.show(truncate=False)
(sentenceDF
 .select(removePunctuation(col('sentence')))
 .show(truncate=False))


//======================================================================
 %pyspark
fileName = "/aaa/Dante\'s_Inferno.txt"
shakespeareDF = sqlContext.read.text(fileName).select(removePunctuation(col('value')))
shakespeareDF.show(20, truncate=False)


//======================================================================
%pyspark
# TODO: Replace <FILL IN> with appropriate code
from pyspark.sql.functions import split, explode
shakeWordsDF = (shakespeareDF
                .select(explode(split('sentence',' ')).alias('word')).where(length('word')>0))

shakeWordsDF.show()
shakeWordsDFCount = shakeWordsDF.count()
print shakeWordsDFCount


//======================================================================
%pyspark
# TODO: Replace <FILL IN> with appropriate code
from pyspark.sql.functions import desc
topWordsAndCountsDF = wordCount(shakeWordsDF).orderBy('count',ascending=False)
topWordsAndCountsDF.show(1000)



