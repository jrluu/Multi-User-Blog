from google.appengine.ext import ndb

class Post(ndb.Model):
    '''Kind for Post'''
    author = ndb.StringProperty(required=True)
    title = ndb.StringProperty()
    content = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    likes = ndb.IntegerProperty(default=0)
    isRoot = ndb.BooleanProperty(default=False)
