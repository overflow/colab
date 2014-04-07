# -*- coding: utf-8 -*-
from django.db import connections
from south.v2 import DataMigration

class Migration(DataMigration):

    def forwards(self, orm):
        # selecting trac database
        connection = connections['mediawiki']

        cursor = connection.cursor()
        cursor.execute('''
        CREATE VIEW mediawiki_view AS 
            select page_title as name, old_text as wiki_text,user_real_name||' ('||rev_user_text||')'
             as author,
             (select string_agg(distinct user_real_name||' ('||rev_user_text||')',',') from mediawiki.mwuser as mwuser,mediawiki.revision as rev2 where user_id=rev2.rev_user and rev_page=rev.rev_page) as collaborators, rev.rev_timestamp as created, rev.rev_timestamp as modified             from mediawiki.mwuser as mwuser2,mediawiki.revision as rev, mediawiki.page as wiki,mediawiki.pagecontent as content  where page_id=rev_page  and content.old_id=rev.rev_text_id and rev.rev_id=(select max(rev_id) from mediawiki.revision where rev_page=wiki.page_id  group by page_id) and mwuser2.user_id=rev_user;
        ''')

    def backwards(self, orm):
        # Selecting trac database
        connection = connections['mediawiki']

        cursor = connection.cursor()
        cursor.execute('''
            DROP VIEW mediawiki_view;
            ''')
    complete_apps = ['proxy']
    symmetrical = True
