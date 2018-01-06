from datetime import datetime

from . import db


class CommonModel(object):
    def _serialize(self):
        """Jsonify the sql alchemy query result."""
        convert = dict()
        d = dict()
        # noinspection PyUnresolvedReferences
        for c in self.__class__.__table__.columns:
            v = getattr(self, c.name)
            if c.type in convert.keys() and v is not None:
                try:
                    d[c.name] = convert[c.type](v)
                except:
                    d[c.name] = "Error: Failed to covert using ", str(
                        convert[c.type])
            elif v is None:
                if hasattr(c.type, '__visit_name__') and c.type.__visit_name__ == 'JSON':
                    d[c.name] = None
                elif "INTEGER" == str(c.type) or "NUMERIC" == str(c.type):
                    # print "??"
                    d[c.name] = 0
                elif "DATETIME" == str(c.type):
                    d[c.name] = None
                else:
                    # print c.type
                    d[c.name] = str()
            elif isinstance(v, datetime):
                if v.utcoffset() is not None:
                    v = v - v.utcoffset()
                d[c.name] = v.strftime('%Y-%m-%d %H:%M:%S')
            else:
                d[c.name] = v
        return d

    def json(self):
        raise NotImplementedError()


class Channel(db.Model, CommonModel):
    __tablename__ = 'channel'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Unicode(64, collation='c'), nullable=False, unique=True)
    dccon_url = db.Column(db.Unicode(512, collation='c'), nullable=True)
    last_cache_update = db.Column(db.DateTime(), nullable=True)
    is_using_cache = db.Column(db.Boolean(), nullable=False, default=False)
    cached_dccon = db.Column(db.JSON(), nullable=True)

    def json(self):
        channel = self._serialize()
        channel.pop('id')
        channel.pop('cached_dccon')
        if self.is_using_cache:
            channel['dccon_url'] = self.cached_dccon_url()
        return channel

    def cached_dccon_url(self):
        return '/api/channel/{}/cached-dccon'.format(self.user_id)
