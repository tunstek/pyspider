import time, requests, json
from pyspider.database.base.projectdb import ProjectDB as BaseProjectDB


class ProjectDB(BaseProjectDB):
    __collection_name__ = 'projectdb'

    def __init__(self, url, database='projectdb'):
        self.url = url + self.__collection_name__ + "_" + database + "/"
        self.database = database
        self.insert('', {})
        # create index
        payload = {
            'index': {
                'fields': ['name'],
                'name': self.__collection_name__ + "_" + database
            }
        }
        res = requests.post(self.base_url + self.__collection_name__ + "_" + database + "/_index", data=payload).json()
        self.index = res['id']
        #self.collection.ensure_index('name', unique=True)

    def _default_fields(self, each):
        if each is None:
            return each
        each.setdefault('group', None)
        each.setdefault('status', 'TODO')
        each.setdefault('script', '')
        each.setdefault('comments', None)
        each.setdefault('rate', 0)
        each.setdefault('burst', 0)
        each.setdefault('updatetime', 0)
        return each

    def insert(self, name, obj={}):
        url = self.url + name
        obj = dict(obj)
        obj['name'] = name
        obj['updatetime'] = time.time()
        res = requests.put(url, data = json.dumps(obj), headers = {"Content-Type": "application/json"}).json()
        return res

    def update(self, name, obj={}, **kwargs):
        # object contains the fields to update and their new values
        update = self.get(name) # update will contain _rev
        if update is None:
            return None
        obj = dict(obj)
        obj['updatetime'] = time.time()
        obj.update(kwargs)
        for key in obj:
            update[key] = obj[key]
        self.insert(name, update)

    def get_all(self, fields=None):
        if fields is None:
            fields = []
        payload = {
            "selector": {},
            "fields": fields,
            "use_index": self.index
        }
        url = self.url + "_find"
        res = requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"}).json()
        for doc in res['docs']:
            yield self._default_fields(doc)

    def get(self, name, fields=None):
        if fields is None:
            fields = []
        payload = {
            "selector": {"name": name},
            "fields": fields,
            "limit": 1,
            "use_index": self.index
        }
        url = self.url + "_find"
        res = requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"}).json()
        if len(res['docs']) == 0:
            return None
        return self._default_fields(res['docs'][0])

    def check_update(self, timestamp, fields=None):
        if fields is None:
            fields = []
        for project in self.get_all(fields=('updatetime', 'name')):
            if project['updatetime'] > timestamp:
                project = self.get(project['name'], fields)
                yield self._default_fields(project)

    def drop(self, name):
        doc = self.get(name)
        payload = {"rev": doc["_rev"]}
        url = self.url + name
        return requests.delete(url, params=payload, headers={"Content-Type": "application/json"}).json()

    def drop_database(self):
        return requests.delete(self.url, headers={"Content-Type": "application/json"}).json()
