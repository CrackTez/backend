from time import time


import time
stringTime = "2022-07-28T07:08:06Z"
# find timestamp of the stringTime
timestamp = round(time.mktime(time.strptime(stringTime, "%Y-%m-%dT%H:%M:%SZ")))
print(timestamp)

# get string time back from timestamp
stringTime = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(timestamp))
print(stringTime)

#write query to select top 10 posts from table after casting idKey to int
#mySqlQuery = f'''SELECT idKey, txnHash, title, author, contentHash, thumbnailHash, fundraising_goal, fundraised FROM {table} WHERE idKey > {int(idKey)} ORDER BY idKey LIMIT 10'''