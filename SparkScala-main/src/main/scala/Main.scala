package SparkScala

import scala.collection.Map
import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.spark.sql.types._
import org.apache.spark.sql.functions.{col, from_json, current_timestamp}
import org.apache.spark.sql.streaming.Trigger

object Main {
  val spark = SparkSession
    .builder()
    .appName("SparkScala")
    .getOrCreate()

  def main(args: Array[String]): Unit = {
    // Development options
    val options = Map(
      "kafka.bootstrap.servers" -> "localhost:29091,localhost:29092,localhost:29093",
      "subscribe" -> "foobar",
      "startingOffsets" -> "latest"
    )

    // Production options
    // val options = Map(
    //   "kafka.bootstrap.servers" -> "10.1.8.29:9092,10.1.8.30:9092,10.1.8.31:9092",
    //   "subscribe" -> "weather-data",
    //   "startingOffsets" -> "latest"
    // )

    val stationDF = getStationDF()

    val rawDF = spark.readStream
      .format("kafka")
      .options(options)
      .load()

    val weatherDataSchema = new StructType()
      .add("StationCode", IntegerType)
      .add("SO2", DoubleType)
      .add("NO2", DoubleType)
      .add("O3", DoubleType)
      .add("CO", DoubleType)
      .add("PM10", DoubleType)
      .add("PM2.5", DoubleType)
      .add("SendTime", TimestampType)

    val weatherDataDF =
      rawDF
        .select(
          from_json(col("value").cast(StringType), weatherDataSchema)
            .as("data")
        )
        .select("data.*")

    val processedDF = weatherDataDF
      .join(
        stationDF.hint("broadcast"),
        weatherDataDF("StationCode") === stationDF("infoStationCode"),
        "left"
      )
      .drop("infoStationCode")

    // Local development codes
    val query = processedDF.writeStream
      .format("parquet")
      .option("checkpointLocation", "/Users/ducth/scala/SparkScala/checkpoint")
      .option("path", "/Users/ducth/scala/SparkScala/weatherData")
      .trigger(Trigger.ProcessingTime("20 seconds"))
      .start()

    // val query = processedDF.writeStream
    //   .format("parquet")
    //   .option("checkpointLocation", "hdfs://master:9090/checkpoint")
    //   .option("path", "hdfs://master:9090/weatherData")
    //   .trigger(Trigger.ProcessingTime("30 seconds"))
    //   .start()

    query.awaitTermination()
  }

  def getStationDF(): DataFrame = {
    val stationInfoSchema = new StructType()
      .add("StationCode", IntegerType)
      .add("Latitude", DoubleType)
      .add("Longitude", DoubleType)

    spark.read
      .option("header", "true")
      .schema(stationInfoSchema)
      .csv("/Users/ducth/scala/SparkScala/station_info.csv")
      .withColumnRenamed("StationCode", "infoStationCode")
  }
}
