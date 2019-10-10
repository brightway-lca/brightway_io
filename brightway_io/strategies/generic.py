# from bw2data import mapping, Database, databases
from ..units import normalize_units as normalize_units_function
from ..errors import StrategyError
from ..utils import dispatch, activity_hash, DEFAULT_FIELDS
# from copy import deepcopy
# import numbers
# import numpy as np
import pprint
import stats_arrays as sa


def format_nonunique_key_error(obj, fields, others):
    template = """Object in source database can't be uniquely linked to target database.\nProblematic dataset is:\n{ds}\nPossible targets include (at least one not shown):\n{targets}"""
    fields_to_print = list(fields or DEFAULT_FIELDS) + ['filename']
    _ = lambda x: {field: x.get(field, "(missing)") for field in fields_to_print}
    return template.format(
        ds=pprint.pformat(_(obj)),
        targets=pprint.pformat([_(x) for x in others])
    )


def drop_attribute(data, key, attribute):
    for obj in data[key]:
        if attribute in obj:
            del obj[attribute]
    return data


def number_objects(data, key, sorting_fields):
    for i, obj in enumerate(sorted(data[key], key=lambda x: [x.get(field) for field in sorting_fields])):
        obj['id'] = i + 1  # SQL sequences are 1-indexed
    return data


def link_iterable_by_fields(source_data, target_data, link_field, source_fields=None, target_fields=None, relink=False):
    """Generic function to link objects in ``unlinked`` to objects in ``other`` using fields ``fields``.

    The database to be linked must have uniqueness for each object for the given ``fields``.

    If ``relink``, link to objects which already have an ``input``. Otherwise, skip already linked objects.

    """
    if not relink:
        filter_func = lambda x: True
    else:
        filter_func = lambda x: not x.get(link_field)

    duplicates, candidates = {}, {}

    if source_fields and target_fields is None:
        target_fields = source_fields
    else:
        if source_fields is None:
            source_fields = DEFAULT_FIELDS
        if target_fields is None:
            target_fields = DEFAULT_FIELDS

    for obj in source_data:
        if 'id' not in obj:
            raise StrategyError(f"Missing id field for object: {obj}")
        key = activity_hash(obj, source_fields)
        if key in candidates:
            duplicates.setdefault(key, []).append(obj)
        else:
            candidates[key] = obj

    for obj in filter(filter_func, target_data):
        key = activity_hash(obj, target_fields)
        if key in duplicates:
            raise StrategyError(format_nonunique_key_error(obj, target_fields, duplicates[key]))
        elif key in candidates:
            obj[link_field] = candidates[key]['id']
    return target_data


def internal_linking(data, source_key, target_key, link_field, *args, **kwargs):
    data[target_key] = link_iterable_by_fields(data[source_key], data[target_key], link_field, *args, **kwargs)
    return data


def assign_only_product_as_production(db):
    """Assign only product as reference product.

    Skips datasets that already have a reference product or no production exchanges. Production exchanges must have a ``name`` and an amount.

    Will replace the following activity fields, if not already specified:

    * 'name' - name of reference product
    * 'unit' - unit of reference product
    * 'production amount' - amount of reference product

    """
    #TODOBW3
    for ds in db:
        if ds.get("reference product"):
            continue
        products = [x for x in ds.get('exchanges', []) if x.get('type') == 'production']
        if len(products) == 1:
            product = products[0]
            assert product['name']
            ds['reference product'] = product['name']
            ds['production amount'] = product['amount']
            ds['name'] = ds.get('name') or product['name']
            ds['unit'] = ds.get('unit') or product.get('unit') or 'Unknown'
    return db


def assign_no_uncertainty(data):
    for obj in data:
        obj['uncertainty_type_id'] = sa.NoUncertainty.id
    return data


# def link_technosphere_by_activity_hash(db, external_db_name=None, fields=None):
#     """Link technosphere exchanges using ``activity_hash`` function.

#     If ``external_db_name``, link against a different database; otherwise link internally.

#     If ``fields``, link using only certain fields."""
#     TECHNOSPHERE_TYPES = {"technosphere", "substitution", "production"}
#     if external_db_name is not None:
#         if external_db_name not in databases:
#             raise StrategyError("Can't find external database {}".format(
#                                 external_db_name))
#         other = (obj for obj in Database(external_db_name)
#                  if obj.get('type', 'process') == 'process')
#         internal = False
#     else:
#         other = None
#         internal = True
#     return link_iterable_by_fields(db, other, internal=internal, kind=TECHNOSPHERE_TYPES, fields=fields)


# def set_code_by_activity_hash(db, overwrite=False):
#     """Use ``activity_hash`` to set dataset code.

#     By default, won't overwrite existing codes, but will if ``overwrite`` is ``True``."""
#     for ds in db:
#         if 'code' not in ds or overwrite:
#             ds['code'] = activity_hash(ds)
#     return db


# def tupleize_categories(db):
#     for ds in db:
#         if ds.get('categories'):
#             ds['categories'] = tuple(ds['categories'])
#         for exc in ds.get('exchanges', []):
#             if exc.get('categories'):
#                 exc['categories'] = tuple(exc['categories'])
#     return db


def drop_unlinked(data):
    """This is the nuclear option - use at your own risk!"""
    data['exchanges'] = [exc
        for exc in data.get('exchanges', [])
        if exc['activity_code'] and exc['flow_code']
    ]
    return data


@dispatch(keys=['flows', 'exchanges'])
def normalize_units(data):
    """Normalize units in datasets and their exchanges"""
    for obj in data:
        obj['unit'] = normalize_units_function(obj.get('unit', ''))
    # for param in ds.get('parameters', {}).values():
    #     if 'unit' in param:
    #         param['unit'] = normalize_units_function(param['unit'])
    return data


# def convert_uncertainty_types_to_integers(db):
#     """Generic number conversion function convert to floats. Return to integers."""
#     for ds in db:
#         for exc in ds['exchanges']:
#             try:
#                 exc['uncertainty type'] = int(exc['uncertainty type'])
#             except:
#                 pass
#     return db


# def drop_falsey_uncertainty_fields_but_keep_zeros(db):
#     """Drop fields like '' but keep zero and NaN.

#     Note that this doesn't strip `False`, which behaves *exactly* like 0.

#     """
#     uncertainty_fields = [
#         'minimum',
#         'maximum',
#         'scale',
#         'shape',
#         'loc',
#     ]

#     def drop_if_appropriate(exc):
#         for field in uncertainty_fields:
#             if field not in exc or exc[field] == 0:
#                 continue
#             elif isinstance(exc[field], numbers.Number) and np.isnan(exc[field]):
#                 continue
#             elif not exc[field]:
#                 del exc[field]

#     for ds in db:
#         for exc in ds['exchanges']:
#             drop_if_appropriate(exc)
#     return db

# def convert_activity_parameters_to_list(data):
#     """Convert activity parameters from dictionary to list of dictionaries"""
#     def _(key, value):
#         dct = deepcopy(value)
#         dct['name'] = key
#         return dct

#     for ds in data:
#         if 'parameters' in ds:
#             ds['parameters'] = [_(x, y) for x, y in ds['parameters'].items()]

#     return data
