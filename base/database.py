import pymongo


def vault():
    """ Connect Vault Database on local MongoDB
    """
    client = pymongo.MongoClient("localhost", 27017)
    return client.vault
