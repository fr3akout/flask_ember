from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKeyConstraint

from .property_builder_base import PropertyBuilderBase


class RelationshipBuilderBase(PropertyBuilderBase):
    def __init__(self, use_list, force_primary_key=False, **kwargs):
        self.use_list = use_list
        self.force_primary_key = force_primary_key
        self.join_clauses = list()
        super().__init__(**kwargs)

    @property
    def target(self):
        return self.resource_property.target

    @property
    def inverse(self):
        return self.resource_property.inverse

    @property
    def target_table(self):
        return self.target._table

    @property
    def foreign_key_builder(self):
        return self.builder

    @property
    def generate_foreign_key(self):
        # Whether foreign keys are generated by this side is not determined
        # for one-to-one relationships when this builder is created.
        # Therefore it has to be evaluated lazily from the underlying property.
        return not self.resource_property.primary

    def get_foreign_key_arguments(self):
        return {
            'onupdate': 'CASCADE'
        }

    def create_non_primary_key_columns(self):
        if not self.generate_foreign_key:
            return

        primary_columns = self.target_table.primary_key.columns
        if not primary_columns:
            raise Exception("No primary key found in table "
                            "'{}' ".format(self.target_table.fullname))

        foreign_key_names = list()
        foreign_key_ref_names = list()

        for primary_column in primary_columns:
            column_name = '{}_{}'.format(self.name,
                                         primary_column.key)
            column = Column(column_name, primary_column.type,
                            primary_key=self.force_primary_key)
            self.foreign_key_builder.add_column(column)

            foreign_key_names.append(column.key)
            foreign_key_ref_names.append('{}.{}'.format(
                self.target_table.fullname, primary_column.key))
            self.join_clauses.append(column == primary_column)

        foreign_key_name = '_'.join(foreign_key_names)
        constraint_name = '{}_{}_fk'.format(self.table.fullname,
                                            foreign_key_name)

        constraint = ForeignKeyConstraint(foreign_key_names,
                                          foreign_key_ref_names,
                                          name=constraint_name,
                                          **self.get_foreign_key_arguments())
        self.foreign_key_builder.add_constraint(constraint)

    def get_relation_arguments(self):
        kwargs = {
            'lazy': 'dynamic' if self.use_list else 'select',
            'uselist': self.use_list,
            'back_populates': self.resource_property.backref
        }
        return kwargs

    def create_properties(self):
        relation = relationship(self.target, **self.get_relation_arguments())
        self.add_mapper_property(self.name, relation)
