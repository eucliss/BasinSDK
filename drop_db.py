from BasinSDK.db import MongoDB

m = MongoDB()
m.setDatabase('BasinSDK')
m.setCollection('Wallets')
m.collection.drop()
m.kill()