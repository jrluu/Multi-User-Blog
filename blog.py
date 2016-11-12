import os
import webapp2
import jinja2
import hashlib
import hmac

from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)


#IDK IF WE WILL NEED THIS
default_account_id = "default_account_id"
default_post_id = "default_post_id"

def account_key(account_id = 'default_account_id'):
    """Constructs a Datascore Key for a Account entity.
        We use account_id as the key.
    """
    return ndb.Key('Accounts', account_id)

def post_key(post_id = 'default_post_id'):
    """Constructs a Datascore Key for a Post entity.
        We use post_id as the key.
    """
    return ndb.Key('Posts', post_id)

#Won't be dynamic, so no ndb.Expando class
class Account(ndb.Model):
    #user = ndb.StringProperty(required = True)
    #the ID will be the user (Key.ID)
    password = ndb.TextProperty(required = True)
    email = ndb.TextProperty()


class Post(ndb.Model):
    author = ndb.StringProperty()
    title = ndb.StringProperty(required = True)
    content = ndb.TextProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    likes = ndb.IntegerProperty(default = 0)
    #Parent = ndb. StructuredProperty()
    '''Need a list of children post'''
    #Child =  ndb. StructuredProperty(repeated = True)


SECRET = "asdf"
def hash_str(s):
    return hmac.new(SECRET,s).hexdigest()

#Takes in some value, and returns "value,hash"
def make_secure_val(s):
    return "%s|%s" %(s, hash_str(s))

#Takes in a string of format "value,hash"
#Return value if true
def check_secure_val(h):
    val = h.split(',')[0]
    if hmac.compare_digest(h, make_secure_val(val)):
        return val


#Takes in a string of format "username,password,verifypw,email"
#Return value if true
#def check_secure_val(var_list_str):
#    val_list = h.split('|')
#    num_of_var = len(val_list)

#    if num_of_var > 2:
#        password = val_list[1]
#        if hmac.compare_digest(password, ):
#            return val


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template,**kw))

    #Cookie should be info=username|password
    #Cookie stuff
    def set_secure_cookie(self, name, val):
        self.response.headers['Content-Type'] = 'text/html'
        cookie_val = str(make_secure_val(val))
#        cookie_val = str(cookie_val)
#        self.response.headers.add_header('Set-Cookie', 'username = %s,password = %s' % (name, cookie_val))
        self.response.headers.add_header('Set-Cookie', 'username = %s' % str(name))
        self.response.headers.add_header('Set-Cookie', 'password = %s' % cookie_val)
    ##Add function that checks if the user is logged in or not

#    def verify_cookie(self):
        ###Check cookie against DB


class SignUpPage(Handler):

    def render_front(self, username = "", password = "", verifypw = "", email = "", errorUser = "", errorPass=""):
        self.render("sign_up.html", username = username, password = password, verifypw = verifypw, email = email, errorUser = errorUser, errorPass= errorPass)

    def get(self):
#        self.set_secure_cookie("Bob_smith", "password_val")
#        cookie_str = self.request.cookies.get("password")
#        self.write(cookie_str)


#        query = Account.get_by_id("Bob")

#        if cookie_str:
#            list_val = cookie_str.split('|')
#            if (len(list_val) == 2):
#                self.write("There are two items here")
        #        name =
            #See amount
            #if there is two
                #name = grabName(list_val[0])
                #if name:
                    #if list_val[1] == grabPw(name)
                        #go to welcome

        self.render_front()


    def post(self):

        username = self.request.get("username")
        password = self.request.get("password")
        verifypw = self.request.get("verifypw")
        email = self.request.get("email")
        errorUser = ""
        errorPass = ""
        redirect = False

        if username and password and verifypw:

            account_query = Account.get_by_id(username)
            email_query = Account.query()

            if account_query:
                errorUser = "Username Taken"
                redirect = True
            if password != verifypw:
                errorPass = "Passwords do not match"
                redirect = True
        else:
            redirect = True
            errorUser = "Please fill out username and password fields"
            errorPass = ""

        if redirect:
            self.render_front(username, password, verifypw, email, errorUser, errorPass)
        else:
#            password = hash_str(password)
            #Create a fake user account
            user= Account(id = username, password=hash_str(password), email = email)
            user.put()
            #Create Cookie
#            password = make_secure_val(password)
#            self.write("This is username: %s and password: %s" % (username, password))
            self.set_secure_cookie(username, password)

        #Erase this later
        self.render_front(username, password, verifypw, email, errorUser, errorPass)

app = webapp2.WSGIApplication([('/', SignUpPage),
                                ],
                                debug=True)
