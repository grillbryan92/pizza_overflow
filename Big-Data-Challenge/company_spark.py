# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 23:34:39 2022

@author: Bryan
"""

from datetime import date, datetime, timedelta
from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext
from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark.sql import SparkSession
import json
import os
os.environ['PYSPARK_SUBMIT_ARGS'] = "--packages=org.apache.hadoop:hadoop-aws:2.7.1 pyspark-shell"

conf = SparkConf().setAppName("something").setMaster("local")
sc = SparkContext.getOrCreate(conf)
sc = SparkSession.builder.master('local[*]').appName('app_name').getOrCreate()
sqlContext = SQLContext(sc)

employeeColumn = ["emp_no", "birth_date", "first_name", "last_name", "gender", "hire_date"]
employeeData = [
    ["10001","1953-09-02","Georgi","Facello","M","1986-06-26"],
    ["10002","1964-06-02","Bezalel","Simmel","F","1985-11-21"],
    ["10003","1959-12-03","Parto","Bamford","M","1986-08-28"],
    ["10004","1954-05-01","Chirstian","Koblick","M","1986-12-01"],
    ["10005","1955-01-21","Kyoichi","Maliniak","M","1989-09-12"]
]
jobColumn = ["emp_no", "title", "from_date" , "to_date"]
jobData = [
    ["10001","Senior Engineer","1986-06-26","9999-01-01"],
    ["10002","Staff","1996-08-03","9999-01-01"],
    ["10003","Senior Engineer","1995-12-03","9999-01-01"],
    ["10004","Senior Engineer","1995-12-01","9999-01-01"],
    ["10005","Senior Staff","1996-09-12","9999-01-01"]
]
salaryColumn = ["emp_no", "salary", "from_date" , "to_date"]
salaryData = [
    ["10001","66074","1988-06-25","1989-06-25"], ["10001","62102","1987-06-26","1988-06-25"], ["10001","60117","1986-06-26","1987-06-26"],
    ["10002","72527","2001-08-02","9999-01-01"], ["10002","71963","2000-08-02","2001-08-02"], ["10002","69366","1999-08-03","2000-08-02"],
    ["10003","43311","2001-12-01","9999-01-01"], ["10003","43699","2000-12-01","2001-12-01"], ["10003","43478","1999-12-02","2000-12-01"],
    ["10004","74057","2001-11-27","9999-01-01"], ["10004","70698","2000-11-27","2001-11-27"], ["10004","69722","1999-11-28","2000-11-27"],
    ["10005","94692","2001-09-09","9999-01-01"], ["10005","91453","2000-09-09","2001-09-09"], ["10005","90531","1999-09-10","2000-09-09"]
]

rdd = sc.sparkContext.parallelize(employeeData)
employees_df = rdd.toDF(employeeColumn)

rdd = sc.sparkContext.parallelize(jobData)
jobs_df = rdd.toDF(jobColumn)

rdd = sc.sparkContext.parallelize(salaryData)
salaries_df = rdd.toDF(salaryColumn)

employees_df = employees_df.withColumn('birth_date', date_format('birth_date', 'd.MMM.yyy'))
employees_df = employees_df.select(*employeeColumn
                                   , concat(employees_df.first_name[0:2],employees_df.last_name,lit("@company.com")).alias('email'))

for col in employeeColumn:
    employees_df = employees_df.withColumnRenamed(col,col.replace('_',' ').capitalize())

for col in jobColumn:
    jobs_df = jobs_df.withColumnRenamed(col,col.replace('_',' ').capitalize())

for col in salaryColumn:
    salaries_df = salaries_df.withColumnRenamed(col,col.replace('_',' ').capitalize())
    
employees_df.createOrReplaceTempView("employees")
jobs_df.createOrReplaceTempView("jobs")
salaries_df.createOrReplaceTempView("salaries")


df2=sqlContext.sql("""
    SELECT j.`Title`, AVG(s.salary) AS average
    FROM jobs j
    LEFT JOIN salaries s ON j.`Emp no` = s.`Emp no`
    GROUP BY 1
    """)
df2.show()
df2.createOrReplaceTempView("avg_salaries")

salaries_df=sqlContext.sql("""
    SELECT s.*
    ,CASE WHEN s.Salary < av.average THEN true ELSE false END as flag
    FROM salaries s
    LEFT JOIN jobs j ON j.`Emp no` = s.`Emp no`
    LEFT JOIN avg_salaries av ON av.`Title` = j.`Title`
    """)

employees_df.show()
jobs_df.show()
salaries_df.show()

