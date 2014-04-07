
class TracRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'proxy':
            return 'trac'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'proxy':
            return 'trac'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'proxy' or \
            obj2._meta.app_label == 'proxy':
            return True
        return None

    def allow_migrate(self, db, model):
        if db == 'trac':
            return model._meta.app_label == 'proxy'
        elif model._meta.app_label == 'proxy':
            False
        return None

class WikiRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.db_table == 'mediawiki_view' or model._meta.db_table=='wiki_collab_count_view':
            return 'mediawiki'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.db_table== 'mediawiki_view' or model._meta.db_table=='wiki_collab_count_view':
            return 'mediawiki'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'proxy' or \
            obj2._meta.app_label == 'proxy':
            return True
        return None

    def allow_migrate(self, db, model):
        if db == 'mediawiki':
            return model._meta.app_label == 'proxy'
        elif model._meta.app_label == 'proxy':
            False
        return None
