
from flask import Flask, request, jsonify
from decouple import config
from flask_mysqldb import MySQL
from flask_cors import CORS
import requests
import time
from app.function import getInsertQuery
application = Flask(__name__)
CORS(application)
application.config['MYSQL_HOST'] = config('MYSQL_HOST')
application.config['MYSQL_USER'] = config('MYSQL_USER')
application.config['MYSQL_PASSWORD'] = config('MYSQL_PASSWORD')
application.config['MYSQL_DB'] = config('MYSQL_DB')
mysql = MySQL(application)
DISCORD_WEBHOOK = config('MAINNET_HOOK')

IPFS_PROVIDERS = ["gateway.pinata.clout",  "gateway.ipfs.io", "cloudflare-ipfs.com", "cf-ipfs.com",
                  "ipfs.io"]


@application.route('/')
def index():
    return "hello world"


@application.route('/get-post-by-id', methods=['POST'])
def get_post_by_id():
    data = request.get_json()
    id = data['id']
    net = data['net']
    table = 'mainnet' if net == 'mainnet' else 'jakartanet'
    cur = mysql.connection.cursor()

    cur.execute(
        f'''SELECT idKey, txnHash, title, author, contentHash, thumbnailHash, fundraising_goal, fundraised, timestampCreated FROM {table} WHERE idKey = "{id}"''')
    dbValues = cur.fetchone()
    contentHash = dbValues[4]
    content = ""
    # for provider in IPFS_PROVIDERS:
    #     try:
    #         # print(contentHash)
    #         resFromIPFS = requests.get(
    #             f'https://{provider}/ipfs/{contentHash}')
    #         # print(resFromIPFS)

    #         if resFromIPFS.status_code == 200:
    #             content = resFromIPFS.text
    #             break
    #     except:
    #         continue
    stringTime = time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.localtime(round(int(dbValues[8]))))
    finalJson = {
        'idKey': dbValues[0],
        'txnHash': dbValues[1],
        'title': dbValues[2],
        'author': dbValues[3],
        'contentHash': contentHash,
        "content": contentHash,
        'thumbnailHash': dbValues[5],
        'fundraising_goal': dbValues[6],
        'fundraised': dbValues[7],
        'timestamp': stringTime

    }
    return jsonify(finalJson)


@application.route('/get-posts-by-author', methods=['POST'])
def get_posts_by_author():

    data = request.get_json()
    author = data['author']
    net = data['net']
    table = 'mainnet' if net == 'mainnet' else 'jakartanet'
    cur = mysql.connection.cursor()

    cur.execute(
        f'''SELECT idKey, txnHash, title, author, contentHash, thumbnailHash, fundraising_goal, fundraised, timestampCreated FROM {table} WHERE author = "{author}"''')
    dbValues = cur.fetchall()
    finalJson = []
    for row in dbValues:
        stringTime = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.localtime(round(int(row[8]))))
        finalJson.append({
            'idKey': row[0],
            'txnHash': row[1],
            'title': row[2],
            'author': row[3],
            'contentHash': row[4],

            'thumbnailHash': row[5],
            'fundraising_goal': row[6],
            'fundraised': row[7],
            'timestamp': stringTime

        })
    return jsonify({"posts": finalJson})


@application.route('/get-feed', methods=['POST'])
def get_feed():
    data = request.get_json()
    net = data['net']
    lastID = data['lastID']
    numToFetch = data['numToFetch']
    table = 'mainnet' if net == 'mainnet' else 'jakartanet'
    mySqlQuery = f''''''
    if lastID == "":
        mySqlQuery = f'''SELECT * FROM {table} ORDER BY (idKey + 1)-1 LIMIT {numToFetch}'''
    else:
        mySqlQuery = f'''SELECT * FROM {table} WHERE (idKey +1 )-1 > {lastID} ORDER BY (idKey + 1)-1 LIMIT {numToFetch}'''
    cur = mysql.connection.cursor()
    cur.execute(mySqlQuery)
    dbValues = cur.fetchall()
    finalJson = []
    for row in dbValues:
        stringTime = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.localtime(round(int(row[8]))))
        finalJson.append({
            'idKey': row[0],
            'txnHash': row[1],
            'title': row[2],
            'author': row[3],
            'contentHash': row[4],

            'thumbnailHash': row[5],
            'fundraising_goal': row[6],
            'fundraised': row[7],
            'timestamp': stringTime

        })
    return jsonify({"posts": finalJson})


@application.route('/sync-testnet', methods=['GET'])
def syncTestnet():
    try:
        selectQuery = f'''SELECT idKey, fundraised FROM jakartanet'''
        cur = mysql.connection.cursor()
        cur.execute(selectQuery)
        dbIDs = cur.fetchall()
        keyMap = {}
        tableName = 'jakartanet'
        contract_address = 'KT1FHtvk6RLLvcxEj94Dd45HGrTP21s6rf9Y'
        for tuples in dbIDs:
            keyMap[tuples[0]] = tuples[1]
        print(keyMap)
        insQuery = getInsertQuery(
            keyMap, tableName, contract_address, 'jakartanet')
        UPDATE_LIST = insQuery['UPDATE']
        INSERT_QUERY = insQuery['INSERT']
        responseJson = {}
        if type(UPDATE_LIST) == list:
            cur.executemany(
                f"UPDATE {tableName} SET fundraised = %s WHERE idKey = %s ", UPDATE_LIST)
            cur.connection.commit()
            responseJson["UPDATE"] = True
        else:
            responseJson["UPDATE"] = False

        if INSERT_QUERY is not None:
            cur.execute(INSERT_QUERY)
            cur.connection.commit()
            responseJson["INSERT"] = True
        else:
            responseJson["INSERT"] = False
        return jsonify(responseJson)
    except Exception as e:
        print(e)
        return jsonify({
            "UPDATE": None,
            "INSERT": None
        })


@application.route('/sync-mainnet', methods=['GET'])
def syncMainnet():
    try:
        selectQuery = f'''SELECT idKey, fundraised FROM mainnet'''
        cur = mysql.connection.cursor()
        cur.execute(selectQuery)
        dbIDs = cur.fetchall()
        keyMap = {}
        tableName = 'mainnet'
        contract_address = 'KT1Q1HQ95PgjSDy7Dk2eGvDfkHyNqGxoFWLi'
        for tuples in dbIDs:
            keyMap[tuples[0]] = tuples[1]
        print(keyMap)
        insQuery = getInsertQuery(
            keyMap, tableName, contract_address, 'mainnet')
        UPDATE_LIST = insQuery['UPDATE']
        INSERT_QUERY = insQuery['INSERT']
        responseJson = {}
        if type(UPDATE_LIST) == list:
            cur.executemany(
                f"UPDATE {tableName} SET fundraised = %s WHERE idKey = %s ", UPDATE_LIST)
            cur.connection.commit()
            responseJson["UPDATE"] = True
        else:
            responseJson["UPDATE"] = False

        if INSERT_QUERY is not None:
            cur.execute(INSERT_QUERY)
            cur.connection.commit()
            responseJson["INSERT"] = True
        else:
            responseJson["INSERT"] = False

        newPostList = insQuery["NEW_POST_LIST"]
        print(newPostList)
        for vals in newPostList:
            idKey = vals['idKey']
            title = vals['title']
            author = vals['author']
            thumbnailURL = vals['thumbnailURL']
            fundraising_goal = vals['fundraising_goal']
            print(thumbnailURL)
            requests.post(
                DISCORD_WEBHOOK,
                json={
                    "embeds": [
                        {
                            "title": title,
                            "url": f'https://writez.xyz/post/{idKey}',
                            "image": {
                                "url": f'https://cloudflare-ipfs.com/ipfs/{thumbnailURL}',
                            },
                            "description": f":white_check_mark: New Post on Writez by `{author}` with a goal of {round(int(fundraising_goal)/1e6)} $XTZ",
                        }
                    ]
                },
            )
        return jsonify(responseJson)
    except Exception as e:
        print(e)
        return jsonify({
            "UPDATE": None,
            "INSERT": None
        })
