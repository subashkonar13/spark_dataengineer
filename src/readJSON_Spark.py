import pandas as pd
import re
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
from pyspark.sql.types import DateType
import ast
from pandas import json_normalize
from pyspark.sql.functions import explode
import warnings
warnings.filterwarnings("ignore")

  
def mask_func(colVal):
    res = colVal.find("@")
    if res >= 0:
       pattern  = ".*" + '@' 
       colVal = re.sub(pattern, '', colVal )
       return colVal
    else:
        return ("*" * (len(colVal)))


  
mask_func_udf = udf(mask_func, StringType())

if __name__=="__main__":
   
  #Create Spark Session
   spark=SparkSession.builder.appName("Read Data from JSON").getOrCreate()
                
#------------Data Collector------------------------------
#Using pandas as it is lightweight
   users_url = "https://619ca0ea68ebaa001753c9b0.mockapi.io/evaluation/dataengineer/jr/v1/users"
   messages_url="https://619ca0ea68ebaa001753c9b0.mockapi.io/evaluation/dataengineer/jr/v1/messages"
   user_data = pd.read_json(users_url)
   messages_data=pd.read_json(messages_url)
   user_data['profile'] = [ast.literal_eval(str(user_data['profile'][i])) for i in user_data.index]
   data1=user_data['profile'].apply(pd.Series)
   user_data = user_data.join(data1).drop(columns='profile')
   

  
#messages_data=messages_data.drop(['message'], inplace=True, axis=1)
   users_df=spark.createDataFrame(user_data)
   messages_df=spark.createDataFrame(messages_data)
   messages_df = messages_df.withColumn("created",messages_df['createdAt'].cast(DateType()))
 #------Total Count of Messages in a day-------------
   count_total_messages=messages_df.groupBy("created").count()
    

#-------Count of Users who didn't received any messages------------
   no_message_count=user_df.join(messages_df,user_df.id !=  messages_df.receiverId,"inner").select("firstName","lastName").distinct().count()

#---------------Masking the PII Data------------------
   t=users_df.select("id","subscription","firstName","lastName","email")
   t=t.withColumn("firstName_masked",mask_func_udf(t["firstName"])).withColumn("lastName_masked",mask_func_udf(t["lastName"])).withColumn("email_masked",mask_func_udf(t["email"]))
   t=t.drop("firstName","lastName","email").withColumnRenamed("firstName_masked","firstName").withColumnRenamed("lastName_masked","lastName").withColumnRenamed("email_masked","email")
   t=t.select(t.id,t.firstName,t.lastName,explode(t.subscription))
   t = t.select(t.id,t.firstName,t.lastName,explode(t.col))
                
#-------------Active Subscription Count--------------
   active_sub_count=t.filter(t.value.contains('Active')).count()
                
#--------------Users Sending messages without Active Subscription------------------                
   rejected_sub_count=t.filter(~t.value.contains('Active')).select("id","firstName","lastName","key","value")
   messages_df=messages_df.drop("id")
   rejected_sub_count=rejected_sub_count.join(messages_df,rejected_sub_count.id == messages_df.senderId,"inner").select("firstName","lastName","key","value","id").filter(rejected_sub_count.key.contains('status')).distinct().count()

#----------------Result-------------
   print("Active Subscription Count is:",active_sub_count)
   print("Count of Users who didn't received any messages is:",no_message_count)
   print("Users Sending messages without Active Subscription:",rejected_sub_count)
   count_total_messages.show(truncate=False)
   spark.stop()
















