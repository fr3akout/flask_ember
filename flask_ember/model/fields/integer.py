from sqlalchemy import types

from .data_field_base import DataFieldBase


class Integer(DataFieldBase):
    __sql_type__ = types.Integer
