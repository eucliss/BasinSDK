import pytest
from BasinSDK.db import MongoDB

DATABASE_NAME='testing'
COLLECTION_NAME='test'

obj = {
    'key1': 'value1',
    'key2': 'value2'
}

obj2 = {
    'key1': 'value21',
    'key2': 'value22'
}

@pytest.fixture
def db():
    db = MongoDB()
    db.setDatabase(DATABASE_NAME)
    db.setCollection(COLLECTION_NAME)
    db.collection.drop()
    # db.dropDatabase()
    return db


def test_set_database(db):
    d = db.setDatabase(DATABASE_NAME)
    assert len(d.list_collection_names()) == 0

def test_set_collection(db):
    db.setDatabase(DATABASE_NAME)
    col = db.setCollection(COLLECTION_NAME)
    assert col.name == COLLECTION_NAME
    count = 0
    for doc in col.find():
        count += 1
    assert count == 0

def test_store_record(db):
    db.storeRecord(obj, DATABASE_NAME, COLLECTION_NAME)
    count = 0
    for doc in db.getAllRecords(DATABASE_NAME, COLLECTION_NAME):
        assert doc['key1'] == 'value1'
        assert doc['key2'] == 'value2'
        count += 1
    assert count == 1

def test_get_all_records(db):
    db.storeRecord(obj, DATABASE_NAME, COLLECTION_NAME)
    db.storeRecord(obj2, DATABASE_NAME, COLLECTION_NAME)


    records = db.getAllRecords(DATABASE_NAME, COLLECTION_NAME)
    assert len(records) == 2

def test_update_record(db):
    res = db.storeRecord(obj, DATABASE_NAME, COLLECTION_NAME)
    _id = res.inserted_id
    newObject = {
        'key1': 'value5',
        'key2': 'value6'
    }
    res = db.updateRecord({'key1': 'value1'}, newObject, DATABASE_NAME, COLLECTION_NAME)
    returnedObj = db.getRecord({'key1': 'value5'}, DATABASE_NAME, COLLECTION_NAME)

    assert returnedObj[0]['_id'] == _id
    assert res.modified_count == 1

def test_update_record_single_value(db):
    db.storeRecord(obj, DATABASE_NAME, COLLECTION_NAME)
    newObject = {
        'key1': 'value5',
    }
    db.updateRecord({'key1': 'value1'}, newObject, DATABASE_NAME, COLLECTION_NAME)
    returnedObj = db.getRecord({'key1': 'value5'}, DATABASE_NAME, COLLECTION_NAME)
    assert len(returnedObj) == 1
    assert returnedObj[0]['key2'] == 'value2'


