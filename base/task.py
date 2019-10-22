import os
import datetime
from uuid import uuid4

from base.database import ops

db = ops()


def start_log(_step):
    time = datetime.datetime.now()
    rec = {"_id": str(uuid4()), "pid": os.getpid(), "start_time": time,
           "done": False, "step": 0, "steps": _step}
    db.tasks.insert(rec)
    return rec["_id"]


def update_log(_id):
    time = datetime.datetime.now()
    rec = {"$inc": {"step": 1}, "$set": {"update_time": time}}
    db.tasks.update({"_id": _id}, rec)
    return


def warning_log(_id, msg):
    db.tasks.update({"_id": _id}, {"$push": {"message": msg}})
    return


def end_log(_id):
    rec = db.tasks.find_one({"_id": _id})
    time = datetime.datetime.now()
    if rec["steps"] - rec["step"] == 0:
        new = {"$set": {"update_time": time, "done": True, "error": False}}
    else:
        new = {"$set": {"update_time": time, "done": True, "error": True}}
    db.tasks.update({"_id": _id}, new)

    return
