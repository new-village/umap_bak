import json


def main(race_id):
    """ Reseve JSON and insert database
    """
    result = {"name": "鈴木太郎", "race_id": race_id}
    return json.dumps(result, ensure_ascii=False)
