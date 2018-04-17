from datetime import datetime, timezone

from sqlalchemy import orm
from sqlalchemy import func

from core.temporal.utils import effective_now


class TemporalQuery(orm.Query):
    def clock(self, entity, period=effective_now()):
        cls = entity._clock

        return self.session.query(cls).filter(
            cls.effective.contains(period),
            cls.entity_id == entity.id
        ).one_or_none()

    def field_history(self, entity, field, clock):
        cls = entity._history[field]

        return self.session.query(cls).filter(
            cls.entity_id == entity.id,
            cls.clock_id == clock.id,
            cls.ticks.contains(clock.ticks),
        ).one_or_none()

    def history(self, period=datetime.now(tz=timezone.utc), version=None, fields=None):
        cls = self.column_descriptions[0]['entity']

        # double check to assert the period exists, otherwise the query
        # will always be resultless.
        if not period:
            period = datetime.now(tz=timezone.utc)

        if not hasattr(cls, 'Temporal'):
            raise Exception("not temporal")

        query = self.options(orm.load_only('id'))\
            .join((cls._clock, cls.id == cls._clock.entity_id))\
            .filter(cls._clock.effective.contains(period))

        for field in fields if fields else cls.Temporal.fields:
            if field.name in ('id', 'meta_instance_id'):
                continue

            f = field.element
            parts = str(f).split(".")
            name = parts[1]
            label = field.name
            history = cls._history[name]
            clock = cls._clock
            ticks_name = f'{name}_ticks'
            query = query\
                .add_column(history.value.label(label))\
                .add_column(func.lower(history.ticks).label(ticks_name))\
                .join(
                    history,
                    (cls.id == history.entity_id)
                    & (history.clock_id == clock.id)
                ,isouter=True)

        return query
