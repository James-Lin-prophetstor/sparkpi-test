%pyspark
from pyspark.sql.functions import lit, concat
from pyspark.sql.functions import length
from pyspark.sql.functions import regexp_replace, trim, col, lower
import time

def wordCount(wordListDF):
    """Creates a DataFrame with word counts.

    Args:
        wordListDF (DataFrame of str): A DataFrame consisting of one string column called 'word'.

    Returns:
        DataFrame of (str, int): A DataFrame containing 'word' and 'count' columns.
    """
    return wordListDF.groupBy('word').count()
    

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

from pyspark.sql.functions import desc
for X in range(0,12,1):
    fileName = "/opt/zeppelin/notebook/Dante\'s_Inferno.txt"
    shakespeareDF = sqlContext.read.text(fileName).select(removePunctuation(col('value')))
    topWordsAndCountsDF = wordCount(shakeWordsDF).orderBy('count',ascending=False)
    topWordsAndCountsDF.show(1000)
    time.sleep(300)