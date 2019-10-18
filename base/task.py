import os
import datetime
from uuid import uuid4

from base.database import ops

db = ops()


def start_log(msg):
    rec = {"_id": str(uuid4()), "pid": os.getpid(), "status": "START"}
    step = {"datetime": datetime.datetime.now(), "message": msg}
    rec["step"] = [step]

    try:
        db.tasks.insert(rec)
    except Exception as e:
        print(e)

    return rec["_id"]


def update_log(_id, status, msg):
    step = {"datetime": datetime.datetime.now(), "message": msg}

    try:
        db.tasks.update({"_id": _id}, {"$push": {"step": step}, "$set": {"status": status}})
    except Exception as e:
        print(e)
    
    return
