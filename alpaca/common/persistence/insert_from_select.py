import sqlalchemy as sql
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import UpdateBase


class InsertFromSelect(UpdateBase):

    def __init__(self, table, values, condition):
        self.table = table
        self.values = values
        self.condition = condition


@compiles(InsertFromSelect)
def visit_insert_from_select(element, compiler, **kwargs):
    columns = []
    values = []
    for column, value in element.values.items():
        columns.append(compiler.process(column, include_table=False))
        values.append(
            sql.bindparam(column.name, value, type_=column.type)
        )
    return 'INSERT INTO {table} ({columns}) {select}'.format(
        table=compiler.process(element.table, asfrom=True),
        columns=', '.join(columns),
        select=compiler.process(sql.select(values).where(element.condition))
    )
