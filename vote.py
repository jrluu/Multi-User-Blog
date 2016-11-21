from google.appengine.ext import ndb

from post import Post

class Vote(ndb.Model):
    '''Kind for Vote'''
    post = ndb.KeyProperty(kind=Post)
    user_id = ndb.StringProperty(required=True)
    value = ndb.IntegerProperty(default=0)
