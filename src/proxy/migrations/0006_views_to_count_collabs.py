# -*- coding: utf-8 -*-
from django.db import connections
from south.v2 import DataMigration
from django.conf import settings

class Migration(DataMigration):

    def forwards(self, orm):
        # Selecting trac database
        connection = connections['trac']

        cursor = connection.cursor()
        cursor.execute('''
            CREATE OR REPLACE VIEW ticket_collab_count_view AS
                SELECT
                    COALESCE (t1.author, t2.author) as author,
                    (COALESCE(t1.count, 0) + COALESCE(t2.count, 0)) as count
                FROM
                    (SELECT author, count(*) as count
                     FROM ticket_change
                     GROUP BY author
                     ORDER BY author
                    ) AS t1
                FULL OUTER JOIN
                    (SELECT reporter as author, count(*) as count
                     FROM ticket
                     GROUP BY reporter
                     ORDER BY reporter
                    ) AS t2
                ON t1.author = t2.author;
        ''')
        if 'mediawiki' in connections:
            connection = connections['mediawiki']
            cursor = connection.cursor()
            cursor.execute(''' 
                CREATE OR REPLACE VIEW wiki_collab_count_view AS
                select mwuser.user_name AS author,count(*) from mediawiki.mwuser as mwuser, mediawiki.revision as rev where mwuser.user_id =rev.rev_user group by mwuser.user_name;
            ''')
        else:
            cursor.execute(''' 
                CREATE OR REPLACE VIEW wiki_collab_count_view AS
                    SELECT author, count(*) from wiki GROUP BY author;
            ''')


    def backwards(self, orm):
        # Selecting trac database
        connection = connections['trac']
        cursor = connection.cursor()
        cursor.execute('''
            DROP VIEW IF EXISTS ticket_collab_count_view;
        ''')
        if 'mediawiki' in connections:
            connection = connections['mediawiki']
            cursor = connection.cursor()
        cursor.execute('''
            DROP VIEW IF EXISTS wiki_colab_count_view
        ''') 

    complete_apps = ['proxy']
    symmetrical = True
