import json

import pymongo
from bson.json_util import JSONOptions, dumps


def vault():
    """ Connect Vault Database on local MongoDB
    """
    client = pymongo.MongoClient("localhost", 27017)
    return client.vault


def ops():
    """ Connect Operations Database on local MongoDB
    """
    client = pymongo.MongoClient("localhost", 27017)
    return client.ops


def conv_dict(_bson):
    options = JSONOptions()
    options.datetime_representation = 2

    rec_str = dumps(_bson, ensure_ascii=False, json_options=options)
    rec_dict = json.loads(rec_str)

    # Normalize Date Field
    for key, val in rec_dict.items():
        if isinstance(val, dict) and ("$date" in val):
            rec_dict[key] = rec_dict[key]["$date"]

    return rec_dict
