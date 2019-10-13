import json
from base import database


def main(race_id):
    """ Reseve JSON and insert database
    """
    db = database.vault()
    result = {"name": "鈴木太郎", "race_id": race_id}
    db.holds.update({"_id": 1}, result, upsert=True)

    return json.dumps(result, ensure_ascii=False)
