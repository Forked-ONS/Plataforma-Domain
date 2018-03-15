from model.query import Query


class QueryService:

    def __init__(self, reference_date, version):
        self.reference_date = reference_date
        self.version = version

    def filter(self, app_id, mapped_entity, entity, projection):
        """ execute a query on domain """
        query = Query(self.reference_date, self.version)
        query.set_query_context(app_id, mapped_entity, entity)
        return Query(self.reference_date, self.version).execute(projection)
