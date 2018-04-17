import json

from mapper.index import Index
from core.component import Component
from utils import regex, typing
import re

class Transform(Component):
    def __init__(self, index):
        self.index = index

    def replace_all_atributes(self, _from, needle, replacement):
        """ replace json attributes """
        return _from.replace(f'"{needle}":', f'"{replacement}":')

    def apply_runtime_fields(self, app_id, map_name, model_list):
        """ apply runtime fields at query result """
        accumulator = dict()
        result = []
        for model in model_list:
            model_json = model.copy()
            model_json['_metadata'] = {'type': map_name}
            self.apply_function_fields(
                model_json, app_id, map_name, accumulator)
            self.apply_metadata_fields(model_json)
            result.append(model_json)
        return result

    def apply_function_fields(self, model_json, app_id, map_name, accumulator):
        """ apply function fields """
        if not self.index.has_functions_map(app_id, map_name):
            return model_json

        functions = self.index.get_functions(app_id, map_name)

        for calc_prop in functions:
            accumulator.setdefault(calc_prop, {})
            model_json[calc_prop] = eval(
                functions[calc_prop]['eval'],
                {"item": model_json, "accumulator": accumulator[calc_prop]})

        return model_json

    def apply_metadata_fields(self, model_json):
        meta_instance_id = model_json.pop('meta_instance_id', None)

        if meta_instance_id:
            model_json['_metadata']['instance_id'] = meta_instance_id

        model_json['_metadata']['branch'] = "master"

    def parse_array_param(self, match_group, query_string):
        """ converts an array parameter into a list of conventional parameters."""
        group = match_group.group()
        should_convert_type = True
        import ipdb; ipdb.set_trace(context=15)
        if group.endswith("!"):
            param = group[1:-1]
            should_convert_type = False
        else:
            param = group[1:]
        query = query_string.pop(param).split(';')
        place_holder = ''

        for index, value in enumerate(query):
            param_name = f'{param}{index}'
            place_holder += f':{param_name},'
            if should_convert_type:
                query_string[param_name] = typing.convert(value)
            else:
                query_string[param_name] = value

        return place_holder[0:-1]

    def remove_unsed_params(self, query_string, filter_clause):
        compiled = re.compile("\[.*?\]")
        args = re.compile(":\w*")
        opt_params = {}
        for optional_param in compiled.findall(filter_clause):
            for attr in args.findall(optional_param):
                opt_params[attr[1:]] = optional_param

        for param in opt_params:
            if not param in query_string:
                filter_clause = filter_clause.replace(opt_params[param],"")

        #TODO faz esse replace apenas com regex
        filter_clause = filter_clause.replace("[","")
        filter_clause = filter_clause.replace("]","")
        filter_clause = filter_clause.strip()
        if filter_clause.startswith("and"):
            filter_clause = filter_clause.replace("and","",1)
            filter_clause = filter_clause.strip()
        if filter_clause.startswith("or"):
            filter_clause = filter_clause.replace("or","",1)
            filter_clause = filter_clause.strip()
        return filter_clause


    def get_filters(self, app_id, map_name, query_string):
        """ apply query filter on domain model """
        filters = self.index.get_filters(app_id, map_name)
        filter_name = query_string.pop('filter', None)
        filter_clause = filters.get(filter_name)

        if not filter_clause:
            return {}
        parser = lambda g: self.parse_array_param(g, query_string)
        filter_clause = self.remove_unsed_params(query_string, filter_clause)
        result = {
            "query": regex.replace("\$\w*!*", filter_clause, parser),
            "params": query_string
        }
        return result

