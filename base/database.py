import json
import pymongo
from datetime import datetime, timedelta
from bson.json_util import JSONOptions, dumps


def vault():
    """ Connect Vault Database on local MongoDB
    """
    client = pymongo.MongoClient("localhost", 27017)
    return client.vault


def ops():
    """ Connect Vault Database on local MongoDB
    """
    client = pymongo.MongoClient("localhost", 27017)
    return client.ops


def to_dict(_bson):
    options = JSONOptions()
    options.datetime_representation = 2

    # Convet BSON to String
    rec_str = dumps(_bson, ensure_ascii=False, json_options=options)
    # Convert String to Dictionary
    rec_dict = json.loads(rec_str)
    # Listing
    rec_list = [rec_dict] if isinstance(rec_dict, dict) else rec_dict
    # Normalize Date Field
    rec = []
    for r in rec_list:
        rec.append(nested_date_normalizer(r))

    return rec


def nested_date_normalizer(_dict):
    for key, val in _dict.items():
        if isinstance(val, dict) and ("$date" in val):
            _dict[key] = _dict[key]["$date"]

    return _dict


def date_condition(_year, _month, _day):
    start = datetime(_year, _month, _day, 0, 0, 0)
    end = start + timedelta(days=1)
    condition = {"$gte": start, "$lt": end}
    return condition
