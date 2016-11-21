from google.appengine.ext import ndb

class Account(ndb.Model):
    '''Kind for Account'''
    password = ndb.TextProperty(required=True)
    email = ndb.TextProperty()
