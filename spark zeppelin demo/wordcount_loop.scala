
// this demo will count the numbers on every words on a file.


for (i <- 1 to 12)
{
val textFile = sc.textFile("file:///aaa/Dante\'s_Inferno.txt")
var wordCount = textFile.flatMap(line => line.split(" ")).map(word => (word, 1)).reduceByKey((a, b) => a + b)
var a = wordCount.collect()
println(a)
Thread sleep 300000
}