
from flask import Flask, request, jsonify
from decouple import config
from flask_mysqldb import MySQL
from flask_cors import CORS
import requests
import time
application = Flask(__name__)
CORS(application)
application.config['MYSQL_HOST'] = config('MYSQL_HOST')
application.config['MYSQL_USER'] = config('MYSQL_USER')
application.config['MYSQL_PASSWORD'] = config('MYSQL_PASSWORD')
application.config['MYSQL_DB'] = config('MYSQL_DB')
mysql = MySQL(application)

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
        mySqlQuery = f'''SELECT * FROM jakartanet ORDER BY (idKey + 1)-1 LIMIT {numToFetch}'''
    else:
        mySqlQuery = f'''SELECT * FROM jakartanet WHERE (idKey +1 )-1 > {lastID} ORDER BY (idKey + 1)-1 LIMIT {numToFetch}'''
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

