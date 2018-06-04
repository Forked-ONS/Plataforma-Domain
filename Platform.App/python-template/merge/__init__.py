import log
from sdk.branch_link import BranchLink
from sdk.process_memory import head
from sqlalchemy import text
from model.domain import *

class MergeBranch:
    def __init__(self, session):
        self.session = session
        self.branch_link = BranchLink()

    def get_event(self, instance_id):
        context = head(instance_id)
        return context.get("event")

    def run(self, instance_id):
        event = self.get_event(instance_id)
        branch_name = event.get("payload",{}).get("branch")
        if not branch_name:
            raise Exception(f"branch name should be passed! received:{branch_name}")

        links = self.branch_link.get_links_by_branch(branch_name)
        for link in links:
            _type = link.entity.lower()
            cls = globals()[_type]
            self.flip_data(cls, self.session, link.branch_name)

        self.session.commit()
        log.info("Running merge branch")

    def flip_data(self, cls, session, branch):
        registers = session.query(cls).filter(text(f"branch = '{branch}'")).all()
        for register in registers:
            if not register.from_id:
                new_instance = cls()
                self.assign(register, new_instance)
                new_instance.branch = "master"
                session.add(new_instance)
            else:
                origin_object = session.query(cls).filter(cls.rid == register.from_id).filter(cls.branch == "master").one()
                self.assign(register, origin_object)
                self.session.add(origin_object)

            register.branch = f"merged:{register.branch}"
            session.add(register)

    def assign(self, _from, _to):
        for k, v in _from.__dict__.items():
            if hasattr(_to, k) and k not in {"_sa_instance_state", "branch", "rid"}:
                setattr(_to, k, v)
