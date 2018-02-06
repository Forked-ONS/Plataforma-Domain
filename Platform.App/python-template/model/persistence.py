from model.domain import *
import log


class Persistence:

    def __init__(self, session):
        self.session = session

    def persist(self, objs):
        """ split object collection into 3 operation list for
            creating, updating, destroying looking for changeTrack
            on each object
        """
        to_create = []
        to_update = []
        to_destroy = []
        for o in objs:
            if not self.is_valid_changed_obj(o):
                continue
            if self.is_to_create(o):
                to_create.append(o)
            elif self.is_to_update(o):
                to_update.append(o)
            elif self.is_to_destroy(o):
                to_destroy.append(o)
        result = list(self.create(to_create))
        result += list(self.update(to_update))
        self.destroy(to_destroy)
        return result

    def create(self, objs):
        for o in objs:
            _type = o["_metadata"]["type"]
            _type = _type.title()
            instance = globals()[_type](**o)
            self.session.add(instance)
            yield instance

        self.session.commit()

    def update(self, objs):
        for o in objs:
            _type = o["_metadata"]["type"]
            _type = _type.title()
            cls = globals()[_type]
            instance = cls(**o)
            del o['_metadata']
            del o['meta_instance_id']
            obj = self.session.query(cls).filter(cls.id == o["id"]).one()
            for k, v in o.items():
                if hasattr(obj, k):
                    setattr(obj, k, v)

            yield instance
        self.session.commit()

    def destroy(self, objs):
        return []

    def is_to_create(self, obj):
        return obj["_metadata"]["changeTrack"] == "create"

    def is_to_update(self, obj):
        return obj["_metadata"]["changeTrack"] == "update" and "id" in obj

    def is_to_destroy(self, obj):
        return obj["_metadata"]["changeTrack"] == "destroy" and "id" in obj

    def is_valid_changed_obj(self, obj):
        if not "_metadata" in obj:
            return False
        if not "changeTrack" in obj["_metadata"]:
            return False
        if obj["_metadata"]["changeTrack"] not in ["create", "update", "destroy"]:
            return False
        return True
