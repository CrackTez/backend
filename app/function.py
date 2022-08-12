import requests
import time
import re


def getInsertQuery(dbKeyList, tableName, contractAddress, net):
    res = requests.get(
        f'https://api.{net}.tzkt.io/v1/contracts/{contractAddress}/bigmaps/posts/keys')

    listValues = res.json()
    newPostList = []
    # print(listValues)
    INSER_QUERY = f'INSERT INTO {tableName} VALUES'
    count = 0
    lenOfListVal = len(listValues)
    foundCount = 0
    changeList = []
    for dicts in listValues:
        count += 1
        idKey = dicts['key']
        if idKey in dbKeyList:
            fundraisedString = str(dicts['value']['fundraised'])
            fundraiseValInDB = str(dbKeyList[str(idKey)])
            if fundraisedString != fundraiseValInDB:
                changeList.append((fundraisedString, str(idKey)))

            continue

        foundCount += 1
        txnHash = dicts['hash']
        value = dicts['value']
        title = value['title']
        author = value['author']
        ipfsURL = value['ipfs_url']

        contentHash = re.findall(r'ipfs/(.*)', ipfsURL)[0]
        fundraised = value['fundraised']

        thumbnailURL = value['thumbnail_url']
        thumbnailHash = re.findall(r'ipfs/(.*)', thumbnailURL)[0]
        fundraising_goal = value['fundraising_goal']
        newPostList.append({
            'idKey': idKey,
            'title': title,
            'author': author,
            'thumbnailURL': thumbnailURL,
            'fundraising_goal': fundraising_goal,

        })
        timestampVar = value['timestamp']
        timestamp = round(time.mktime(time.strptime(
            timestampVar, "%Y-%m-%dT%H:%M:%SZ")))

        tempQueryVal = f'("{idKey}", "{txnHash}", "{title}", "{author}", "{contentHash}", "{thumbnailHash}", "{fundraising_goal}", "{fundraised}", "{timestamp}"),'

        INSER_QUERY += tempQueryVal

    returnObj = {
        "NEW_POST_LIST": newPostList,
    }

    if len(changeList) > 0:
        returnObj["UPDATE"] = changeList
    else:
        returnObj["UPDATE"] = None

    if foundCount > 0:
        returnObj["INSERT"] = INSER_QUERY[0:len(INSER_QUERY)-1]
    else:
        returnObj["INSERT"] = None

    return returnObj
