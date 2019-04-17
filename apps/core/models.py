import datetime

from sqlalchemy import Column, Integer, DateTime

from apps import db


class BaseModel(db.Model):
    """ Base app model. """

    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)

    @classmethod
    def get_plural_name(cls):
        """
        Capitalized plural model name.
        :rtype: str
        """

        return cls.__tablename__.capitalize()

    def save(self):
        """ Save current instance. """

        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """ Update current instance by data. """

        for key, item in data.items():
            setattr(self, key, item)
        db.session.commit()

    def delete(self):
        """ Delete current instance. """

        db.session.delete(self)
        db.session.commit()

    def __repr__(self, identity):
        return f"<{self.__class__.__name__} {identity} id:{self.id}>"


class DateTimeModel(BaseModel):
    """ Model with created_at and updated_at fields. """

    __abstract__ = True

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    def update(self, data):
        """ Set updatad_at before doing update. """

        data["updated_at"] = datetime.datetime.utcnow()
        super().update(data)
