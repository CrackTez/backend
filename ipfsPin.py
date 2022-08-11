import requests
import base64
import deso
import re
desoUser = deso.Posts()
userPosts = desoUser.getPostsForPublicKey(
    username="noun141", numToFetch=700).json()
postList = userPosts['Posts']
key = "D734AEE0BCBDCEDA9ABE"
secret = "V2IWwM7mywVrVFS7HxL0gQVKhHrhMIUe19WihAHk"
bucketName = "writez-bucket"
base64Encode = base64.b64encode(
    bytes(f"{key}:{secret}:{bucketName}", 'utf-8')).decode('utf-8')
headerobj = {
    "Authorization": f"Bearer {base64Encode}",
    "Content-Type": "application/json"
}
count = 1
for post in postList:
    isNFT = post['IsNFT']
    if isNFT:
        try:
            imgURL = post['ImageURLs'][0]
            # fetch the CID hash after .org/
            count += 1
            print(count)
            # fetch hash from imgURL
            imgHash = imgURL.split("/")[-1]
            if len(imgHash) == 46:
                print(imgHash)
                payload = {
                    "cid": imgHash,
                    "name": f'{imgHash}',
                    "meta": {
                        "key_name": "tempName"
                    }
                }

                res = requests.post('https://api.filebase.io/v1/ipfs/pins',
                                    json=payload, headers=headerobj)

                print(res.json())

        except Exception as e:
            print(f'no image {e}')
