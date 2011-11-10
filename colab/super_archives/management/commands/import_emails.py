#!/usr/bin/env python
# -*- encoding: utf8 -*-

"""Import emails from a mailman storage to the django database."""

import os
import re
import mailbox
from optparse import make_option

from django.db import transaction
from django.template.defaultfilters import slugify
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from super_archives.models import MailingList, Message, Thread, EmailAddress
from super_archives.management.commands.message import Message as CustomMessage


class Command(BaseCommand, object):
    """Get emails from mailman archives and import them in the django db. """

    help = __doc__
    
    default_archives_path = '/var/lib/mailman/archives/private'
    RE_SUBJECT_CLEAN = re.compile('((re|res|fw|fwd|en|enc):)|\[.*?\]',
                                                                re.IGNORECASE)
    THREAD_CACHE = {}
    EMAIL_ADDR_CACHE = {}
    
    # A new command line option to get the dump file to parse.
    option_list = BaseCommand.option_list + (
        make_option('--archives_path',
            dest='archives_path',
            help='Path of email archives to be imported. (default: %s)' % 
                                                    default_archives_path,
            default=default_archives_path),
            
        make_option('--all',
            dest='all',
            help='Import all messages (default: False)',
            action="store_true",
            default=False),
    )
    
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def log(self, msg, error=False):
        """Log message helper."""
        output = self.stdout
        if error:
            output = self.stderr

        output.write(msg)
        output.write('\n')

    def parse_emails(self, email_filename, index=0):
        """Generator function that parse and extract emails from the file
        `email_filename` starting from the position `index`.

        Yield: An instance of `mailbox.mboxMessage` for each email in the
        file.
        
        """
        self.log("Parsing email dump: %s." % email_filename)
        mbox = mailbox.mbox(email_filename, factory=CustomMessage)
        
        # Get each email from mbox file
        #
        #   The following implementation was used because the object
        #   mbox does not support slicing. Converting the object to a 
        #   tuple (as represented in the code down here) was a valid 
        #   option but its performance was too poor.
        # 
        #for message in tuple(mbox)[index:]:
        #    yield message
        #
        key = index
        while mbox.has_key(key):
            key += 1
            yield key-1, mbox[key-1]

    def get_emails(self, mailinglist_dir, all):
        """Generator function that get the emails from each mailing
        list dump dirctory. If `all` is set to True all the emails in the 
        mbox will be imported if not it will just resume from the last 
        message previously imported.

        Yield: A tuple in the form: (mailing list name, email message).

        """
        self.log("Getting emails dumps from: %s" % mailinglist_dir)
        
        # Get the list of directories ending with .mbox
        mailing_lists_mboxes = (mbox for mbox in os.listdir(mailinglist_dir) 
                                if mbox.endswith('.mbox'))
        
        # Get messages from each mbox
        for mbox in mailing_lists_mboxes:
            mbox_path = os.path.join(mailinglist_dir, mbox, mbox)
            mailinglist_name = mbox.split('.')[0]
            
            # Find the index of the last imported message
            if all:
                n_msgs = 0
            else:
                try:
                    mailinglist = MailingList.objects.get(
                                                    name=mailinglist_name)
                    n_msgs = mailinglist.last_imported_index
                except MailingList.DoesNotExist:
                    n_msgs = 0
            
            for index, msg in self.parse_emails(mbox_path, n_msgs):
                yield mailinglist_name, msg, index

    def get_thread(self, email):
        """Group messages by thread looking for similar subjects"""
        
        subject_slug = slugify(email.subject_clean)
        thread = self.THREAD_CACHE.get(subject_slug)
        if thread is None:
            thread = Thread.objects.get_or_create(
                mailinglist=email.mailinglist,
                subject_token=subject_slug
            )[0]

            self.THREAD_CACHE[subject_slug] = thread

        thread.latest_message = email
        thread.save()        
        return thread
        
    def save_email(self, list_name, email_msg, index):
        """Save email message into the database."""
        
        # Update last imported message into the DB
        mailinglist = MailingList.objects.get_or_create(name=list_name)[0]
        mailinglist.last_imported_index = index
        
        try:
            # If the message is already at the database don't do anything
            Message.objects.get(message_id=email_msg.get('Message-ID'))
        except ObjectDoesNotExist:
            self.create_email(mailinglist, email_msg)
        
        mailinglist.save() 

    def create_email(self, mailinglist, email_msg):

        real_name, from_ = email_msg.get_from_addr()

        email_addr = self.EMAIL_ADDR_CACHE.get(from_)
        if email_addr is None:
            email_addr = EmailAddress.objects.get_or_create(
                address=from_,
                real_name=real_name[:64]
            )[0]
            
            self.EMAIL_ADDR_CACHE[from_] = email_addr

        if not email_addr.real_name and real_name:
            email_addr.real_name = real_name[:64]
            email_addr.save()

        subject = email_msg.get_subject()

        email = Message.objects.create(
            message_id=email_msg.get('Message-ID'),
            from_address=email_addr,
            mailinglist=mailinglist,
            subject=subject,
            subject_clean=self.RE_SUBJECT_CLEAN.sub('', subject).strip(),
            body=email_msg.get_body(),
            received_time=email_msg.get_received_datetime(),
        )
        email.thread = self.get_thread(email)
        email.save()

    @transaction.commit_manually    
    def import_emails(self, archives_path, all):
        """Get emails from the filesystem from the `archives_path` 
        and store them into the database. If `all` is set to True all 
        the filesystem storage will be imported otherwise the importation
        will resume from the last message previously imported.
        
        """
        
        count = 0
        for mailinglist_name, msg, index in self.get_emails(archives_path, all):
            try:
                self.save_email(mailinglist_name, msg, index)
            except:
                # This anti-pattern is needed to avoid the transations to 
                #   get stuck in case of errors.
                transaction.rollback()
                raise
                
            count += 1
            if count % 1000 == 0:
                transaction.commit()
        
        transaction.commit()
        
    def handle(self, *args, **options):
        """Main command method."""
        
        archives_path = options.get('archives_path')
        self.log('Using archives_path `%s`' % self.default_archives_path)
                                                            
        if not os.path.exists(archives_path):
            raise CommandError('archives_path (%s) does not exist' %
                                                                archives_path)
        
        self.import_emails(archives_path, options.get('all'))
        