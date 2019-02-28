%spark

// this demo will count the numbers on every words on a file.

val textFile = sc.textFile("file:///aaa/Dante\'s_Inferno.txt")
val wordCount = textFile.flatMap(line => line.split(" ")).map(word => (word, 1)).reduceByKey((a, b) => a + b)
var r = wordCount.collect()
println 