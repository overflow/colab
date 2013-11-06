# -*- coding: utf-8 -*-

from uuid import uuid4
from hashlib import md5

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.translation import ugettext_lazy as _

from html2text import html2text
from haystack.query import SearchQuerySet
from taggit.managers import TaggableManager
from hitcounter.models import HitCounterModelMixin

from .utils import blocks
from .utils.etiquetador import etiquetador


User = get_user_model()


class NotSpamManager(models.Manager):
    """Only return objects which are not marked as spam."""

    def get_query_set(self):
        return super(NotSpamManager, self).get_query_set().exclude(spam=True)


class EmailAddressValidation(models.Model):
    address = models.EmailField(unique=True)
    user = models.ForeignKey(User, null=True,
                             related_name='emails_not_validated')
    validation_key = models.CharField(max_length=32, null=True,
                                      default=lambda: uuid4().hex)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'address')


class EmailAddress(models.Model):
    user = models.ForeignKey(User, null=True, related_name='emails',
                             on_delete=models.SET_NULL)
    address = models.EmailField(unique=True)
    real_name = models.CharField(max_length=64, blank=True, db_index=True)
    md5 = models.CharField(max_length=32, null=True)

    class Meta:
        ordering = ('id', )

    def save(self, *args, **kwargs):
        self.md5 = md5(self.address).hexdigest()
        super(EmailAddress, self).save(*args, **kwargs)

    def get_full_name(self):
        if self.user and self.user.get_full_name():
            return self.user.get_full_name()
        else:
            return self.real_name

    def get_full_name_or_anonymous(self):
        return self.get_full_name() or _('Anonymous')

    def __unicode__(self):
        return '"%s" <%s>' % (self.get_full_name(), self.address)


class MailingList(models.Model):
    name = models.CharField(max_length=80)
    email = models.EmailField()
    description = models.TextField()
    logo = models.FileField(upload_to='list_logo') #TODO
    last_imported_index = models.IntegerField(default=0)

    def get_absolute_url(self):
        return u'{}?list={}'.format(reverse('thread_list'), self.name)

    def __unicode__(self):
        return self.name


class MailingListMembership(models.Model):
    user = models.ForeignKey(User)
    mailinglist = models.ForeignKey(MailingList)

    def __unicode__(self):
        return '%s on %s' % (self.user.email, self.mailinglist.name)


class Keyword(models.Model):
    keyword = models.CharField(max_length='128')
    weight = models.IntegerField(default=0)
    thread = models.ForeignKey('Thread')

    class Meta:
        ordering = ('?', ) # random order

    def __unicode__(self):
        return self.keyword


class Thread(models.Model, HitCounterModelMixin):

    subject_token = models.CharField(max_length=512)
    mailinglist = models.ForeignKey(MailingList,
                                    verbose_name=_(u"Mailing List"),
                                    help_text=_(u"The Mailing List where is the thread"))
    latest_message = models.OneToOneField('Message', null=True,
                                                     related_name='+',
                                                     verbose_name=_(u"Latest message"),
                                                     help_text=_(u"Latest message posted"))
    score = models.IntegerField(default=0, verbose_name=_(u"Score"), help_text=_(u"Thread score"))
    spam = models.BooleanField(default=False)

    all_objects = models.Manager()
    objects = NotSpamManager()
    tags = TaggableManager()

    class Meta:
        verbose_name = _(u"Thread")
        verbose_name_plural = _(u"Threads")
        unique_together = ('subject_token', 'mailinglist')

    @models.permalink
    def get_absolute_url(self):
        return ('thread_view', [self.mailinglist, self.subject_token])

    def update_keywords(self):
        blocks = MessageBlock.objects.filter(message__thread__pk=self.pk,
                                             is_reply=False)

        self.tags.clear()

        text = u'\n'.join(map(unicode, blocks))
        tags = etiquetador(html2text(text))

        for tag, weight in tags:
            keyword, created = Keyword.objects.get_or_create(thread=self,
                                                             keyword=tag)
            if created or keyword.weight != weight:
                keyword.weight = weight
                keyword.save()

            if weight >= 3:
                self.tags.add(tag)

        # removing old tags not used anylonger
        if tags:
            qs = Keyword.objects.filter(thread=self)
            qs = qs.exclude(keyword__in=zip(*tags)[0])
            qs.delete()

    def get_related(self):
        query_string = u' '.join(self.tags.names())
        if query_string:
            query_set = SearchQuerySet().exclude(django_id=self.pk)
            return query_set.filter(content=query_string, type='thread')

        return tuple()

    def save(self, *args, **kwargs):
        super(Thread, self).save(*args, **kwargs)
        self.update_keywords()

    def __unicode__(self):
        return '%s - %s (%s)' % (self.id,
                                 self.subject_token,
                                 self.message_set.count())

    def update_score(self):
        """Update the relevance score for this thread.

        The score is calculated with the following variables:

        * vote_weight: 100 - (minus) 1 for each 3 days since
          voted with minimum of 5.
        * replies_weight: 300 - (minus) 1 for each 3 days since
          replied with minimum of 5.
        * page_view_weight: 10.

        * vote_score: sum(vote_weight)
        * replies_score: sum(replies_weight)
        * page_view_score: sum(page_view_weight)

        * score = (vote_score + replies_score + page_view_score) // 10
        with minimum of 0 and maximum of 5000

        """

        if not self.subject_token:
            return

        # Save this pseudo now to avoid calling the
        #   function N times in the loops below
        now = timezone.now()
        days_ago = lambda date: (now - date).days
        get_score = lambda weight, created: \
                                  max(weight - (days_ago(created) // 3), 5)

        vote_score = 0
        replies_score = 0
        for msg in self.message_set.all():
            # Calculate replies_score
            replies_score += get_score(300, msg.received_time)

            # Calculate vote_score
            for vote in msg.vote_set.all():
                vote_score += get_score(100, vote.created)

        # Calculate page_view_score
        page_view_score = self.hits * 10

        self.score = (page_view_score + vote_score + replies_score) // 10
        self.save()


class Vote(models.Model):
    user = models.ForeignKey(User)
    message = models.ForeignKey('Message')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'message')

    def __unicode__(self):
        return 'Vote on %s by %s' % (self.Message.id,
                                     self.user.username)


class Message(models.Model):

    from_address = models.ForeignKey(EmailAddress, db_index=True)
    thread = models.ForeignKey(Thread, null=True, db_index=True)
    # RFC 2822 recommends to use 78 chars + CRLF (so 80 chars) for
    #   the max_length of a subject but most of implementations
    #   goes for 256. We use 512 just in case.
    subject = models.CharField(max_length=512, db_index=True,
                               verbose_name=_(u"Subject"),
                               help_text=_(u"Please enter a message subject"))
    subject_clean = models.CharField(max_length=512, db_index=True)
    body = models.TextField(default='',
                            verbose_name=_(u"Message body"),
                            help_text=_(u"Please enter a message body"))
    received_time = models.DateTimeField(db_index=True)
    message_id = models.CharField(max_length=512)
    spam = models.BooleanField(default=False)

    all_objects = models.Manager()
    objects = NotSpamManager()

    class Meta:
        verbose_name = _(u"Message")
        verbose_name_plural = _(u"Messages")
        unique_together = ('thread', 'message_id')
        ordering = ('received_time', )

    def __unicode__(self):
        return '(%s) %s: %s' % (self.id,
                                self.from_address.get_full_name(),
                                self.subject_clean)

    def update_blocks(self):
        # delete all blocks for that message
        self.blocks.all().delete()

        for i, block in enumerate(blocks.EmailBlockParser(self)):
            MessageBlock.from_emailblock(block, self, i)

    @property
    def mailinglist(self):
        if not self.thread:
            return None

        return self.thread.mailinglist

    def vote_list(self):
        """Return a list of user that voted in this message."""
        return [vote.user for vote in self.vote_set.iterator()]

    def votes_count(self):
        return len(self.vote_list())

    def vote(self, user):
        Vote.objects.create(
            message=self,
            user=user
        )

    def unvote(self, user):
        Vote.objects.get(
            message=self,
            user=user
        ).delete()

    @property
    def url(self):
        """Shortcut to get thread url"""
        return reverse('thread_view', args=[self.mailinglist.name,
                                            self.thread.subject_token])

    @property
    def description(self):
        """Alias to self.body"""
        return self.body

    @property
    def title(self):
        """Alias to self.subject_clean"""
        return self.subject_clean

    @property
    def modified(self):
        """Alias to self.modified"""
        return self.received_time

    @property
    def tag(self):
        if not self.thread:
            return None
        return self.mailinglist.name

    @property
    def author(self):
        return self.from_address.get_full_name()

    @property
    def author_url(self):
        return self.from_address.user.get_absolute_url()

    @property
    def icon_name(self):
        return u'envelope'

    @property
    def type(self):
        return u'thread'


class MessageBlock(models.Model):
    message = models.ForeignKey(Message, related_name='blocks')
    text = models.TextField()
    is_reply = models.BooleanField()
    order = models.IntegerField()

    def __unicode__(self):
        return self.text

    class Meta:
        ordering = ('order', )

    @classmethod
    def from_emailblock(klass, emailblock, message, order):
        obj = klass.objects.create(text=emailblock.text,
                                   is_reply=emailblock.is_reply,
                                   message=message,
                                   order=order)
        return obj



class MessageMetadata(models.Model):
    Message = models.ForeignKey(Message)
    # Same problem here than on subjects. Read comment above
    #   on Message.subject
    name = models.CharField(max_length=512)
    value = models.TextField()

    def __unicode__(self):
        return 'Email Message Id: %s - %s: %s' % (self.Message.id,
                                                  self.name, self.value)

