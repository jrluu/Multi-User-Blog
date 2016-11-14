import os
import webapp2
import jinja2
import hashlib
import hmac
import time
import urllib
from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)



SECRET = "SamSmith"
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



#IDK IF WE WILL NEED THIS
default_account_id = "default_account_id"
default_post_id = "default_post_id"

def get_account_key(account_id = 'default_account_id'):
    """Constructs a Datascore Key for a Account entity.
        We use account_id as the key.
    """
    return ndb.Key('Account', account_id)

def get_post_key(post_id = 'default_post_id'):
    """Constructs a Datascore Key for a Post entity.
        We use post_id as the key.
    """
    return ndb.Key('Post', post_id)


#Won't be dynamic, so no ndb.Expando class
class Account(ndb.Model):
    #user = ndb.StringProperty(required = True)
    #the ID will be the user (Key.ID)
    password = ndb.TextProperty(required = True)
    email = ndb.TextProperty()


class Post(ndb.Model):
    author = ndb.StringProperty(required= True)
    title = ndb.StringProperty(required = True)
    content = ndb.TextProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    likes = ndb.IntegerProperty(default = 0)
    isRoot = ndb.BooleanProperty(default = False)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template,**kw))

    def set_secure_cookie(self, name, val):
        self.response.headers['Content-Type'] = 'text/html'
        cookie_val = str(hash_str(val))
        self.response.headers.add_header('Set-Cookie', 'username = %s' % str(name))
        self.response.headers.add_header('Set-Cookie', 'password = %s' % cookie_val)

    def check_cookie(self):
        username = self.request.cookies.get("username")
        password = self.request.cookies.get("password")

        if username:
            account_query = Account.get_by_id(username)
            if account_query:
                if account_query.password:
                    if account_query.password == password:
                        return True

        return False

    def clear_cooke(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.headers.add_header('Set-Cookie', "username = ")
        self.response.headers.add_header('Set-Cookie', "password = ")


class InvalidCookiePage(Handler):
    def get(self):
        self.render("invalidCookie.html")


class PostPage(Handler):
    def render_front(self, username = "", password = ""):

        if not self.check_cookie():
            self.redirect('/invalidCookie')

        post_query = Post.query(Post.isRoot == True).order(-Post.created).fetch(10)
        self.render("post.html", post_query = post_query, username = username, password = password)

    def get(self):
        self.render_front()

    def post(self):

        if not self.check_cookie():
            self.redirect('/invalidCookie')

        username = self.request.cookies.get("username")
        title = self.request.get("title")
        content = self.request.get("content")

        post_key = Post(author = username, title = title, content = content, isRoot = True)
        post_key.put()

        self.render_front()


class SignUpPage(Handler):

    def render_front(self, username = "", password = "", verifypw = "", email = "", errorUser = "", errorPass=""):
        self.render("sign_up.html", username = username, password = password,
                    verifypw = verifypw, email = email, errorUser = errorUser,
                    errorPass= errorPass)

    def get(self):
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

            if account_query:
                errorUser = "Username Taken"
                redirect = True
            if password != verifypw:
                errorPass = "Passwords do not match"
                redirect = True
        else:
            #Taken care of this case with required html form
            #but leaving as redundancy
            redirect = True
            errorUser = "Please fill out username and password fields"
            errorPass = ""

        if redirect:
            self.render_front(username, password, verifypw, email, errorUser, errorPass)
        else:
            user= Account(id = username, password=hash_str(password), email = email)
            user.put()
            self.set_secure_cookie(username, password)
            self.redirect('/welcome')


class LoginPage(Handler):

    def render_front(self, username="", password="", error=""):
        self.render("login.html", username = username, password = password, error=error)

    def get(self):
        self.render_front()

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")

        if username and password:
            account_query = Account.get_by_id(username)

            if account_query:
                if account_query.password:
                    if account_query.password == hash_str(password):
                        self.set_secure_cookie(username,password)
                        self.redirect('/welcome')

        self.render_front(username, password, "Invalid Username or Password")


class LogoutPage(Handler):
    def get(self):
        self.clear_cooke()
        self.redirect('signup')


class WelcomePage(Handler):

    def render_front(self):

        if not self.check_cookie():
            self.redirect('/invalidCookie')

        username = self.request.cookies.get("username")
        self.render("welcome.html", username=username)

    def get(self):
        self.render_front()


class BlogPostPage(Handler):

    def render_front(self, blog_query = "", comments = ""):
        self.render("blogPost.html", blog_query = blog_query, comments = comments, not_found ="")

    def render_not_found(self):
        self.render("blogPost.html", not_found = "Sorry, post not found!")

    def get(self):
        blog_post_id = self.request.get('blog_post_id', default_post_id)

        #Must turn blog_post_id into an int because header gives a string
        blog_query = Post.get_by_id(int(blog_post_id))

        if blog_query:
            blog_query_key = blog_query.key

            comments_query = Post.query(Post.isRoot == False,
                ancestor=blog_query_key).order(-Post.created)
            comments = comments_query.fetch(10)
            self.render_front(blog_query, comments)

        else:
            self.render_not_found()


    def post(self):
        if not self.check_cookie():
            self.redirect('/invalidCookie')

        username = self.request.cookies.get("username")
        title = self.request.get("title")
        content = self.request.get("content")

        blog_post_id = int(self.request.get('blog_post_id'))
        query_params = {'blog_post_id': blog_post_id}

        parent_post_key = Post.get_by_id(blog_post_id).key
#        parent_post_key = get_post_key(blog_post_id)

#        self.write(parent_post_key_default)

#        self.write(parent_post_key)

        post_key = Post(parent = parent_post_key, author = username, title = title, content = content)
        post_key.put()


        self.redirect('/blogPost?' + urllib.urlencode(query_params))

#    def

app = webapp2.WSGIApplication([('/', PostPage),
                                ('/signup', SignUpPage),
                                ('/invalidCookie', InvalidCookiePage),
                                ('/login', LoginPage ),
                                ('/welcome', WelcomePage),
                                ('/logout', LogoutPage),
                                ('/blogPost', BlogPostPage),

                                ],
                                debug=True)
