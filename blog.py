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

'''
Kind Information
(Kind is a group of entities or similarly, tables in SQL)
 '''
default_post_id = 1111111111111111

def post_key(post_id=default_post_id):
    """Constructs a Datastore key for a Post entity.

    We use post_id as the key.
    """
    return ndb.Key('Post', post_id)

#Account Kind
class Account(ndb.Model):
    #the ID will be the user (Key.ID)
    password = ndb.TextProperty(required = True)
    email = ndb.TextProperty()

#Post Kind
class Post(ndb.Model):
    author = ndb.StringProperty(required= True)
    title = ndb.StringProperty()
    content = ndb.TextProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    likes = ndb.IntegerProperty(default = 0)
    isRoot = ndb.BooleanProperty(default = False)

class Vote(ndb.Model):
    post = ndb.KeyProperty( kind  = Post)
    #thought about making an array of user_id, but
    #entity have a limit of 1 MB or 20,000 index
    user_id = ndb.StringProperty( required = True)
    value = ndb.IntegerProperty(default = 0)

"""
Base Handler Class
Takes care of page rendering, cookies maniupulation, and header
"""
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template,**kw))

    #Set username and password(hashed version) into cookie
    def set_secure_cookie(self, name, val):
        self.response.headers['Content-Type'] = 'text/html'
        cookie_val = str(hash_str(val))
        self.response.headers.add_header('Set-Cookie', 'username = %s' % str(name))
        self.response.headers.add_header('Set-Cookie', 'password = %s' % cookie_val)

    #Checks cookie username and password against database
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

    #Clears Cookie
    def clear_cooke(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.headers.add_header('Set-Cookie', "username = ")
        self.response.headers.add_header('Set-Cookie', "password = ")

    #Checks input name with stored Cookie's username
    #NOTE: Should check_cookie first
    def isOwner(self, name):
        username = self.request.cookies.get("username")
        if username:
            if username == name:
                return True

        return False

    def render_not_found(self):
        self.render("notFound.html")

    '''Takes blog_query_id and parent from the header
        Then looks for it in post.
        If not found, return "None"
    '''
    def find_blog_query(self):

        blog_post_id = int(self.request.get('blog_post_id', default_post_id))

        #Creates a parent query and checks if it exists
        parent_id = int(self.request.get('parent', default_post_id))
        parent_query = Post.get_by_id(parent_id)
        if parent_query:
            parent_key = parent_query.key
            blog_query = Post.get_by_id(blog_post_id, parent_key)
        else:
            blog_query = Post.get_by_id(blog_post_id)

        return blog_query

'''Classes of Pages '''
class InvalidCookiePage(Handler):
    def get(self):
        self.render("invalidCookie.html")
#Displays 10 most recent post
class FrontPage(Handler):
    def render_front(self):
        post_query = Post.query(Post.isRoot == True).order(-Post.created).fetch(10)
        self.render("frontPage.html", post_query = post_query)

    def get(self):
        self.render_front()

# Allows users to post a blog
class CreatePostPage(Handler):
    def render_front(self):
        if not self.check_cookie():
            self.redirect('/invalidCookie')

        self.render("post.html")

    def get(self):
        self.render_front()

    def post(self):
        if not self.check_cookie():
            self.redirect('/invalidCookie')

        username = self.request.cookies.get("username")
        title = self.request.get("title")
        content = self.request.get("content")

        post_obj = Post(author = username, title = title, content = content,
                        isRoot = True)
        post_obj.put()

        blog_query_id = post_obj.key.id()
        query_params = {'blog_post_id': blog_query_id}
        self.redirect('/blogPost?' + urllib.urlencode(query_params))


#Takes care of the page where users can sign up
class SignUpPage(Handler):

    def render_front(self, username = "", password = "", verifypw = "",
                     email = "", errorUser = "", errorPass = ""):
        self.render("sign_up.html", username = username, password = password,
                    verifypw = verifypw, email = email, errorUser = errorUser,
                    errorPass = errorPass)

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


#Takes care of users login
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


#Takes care of user logout by clearing cookie
class LogoutPage(Handler):
    def get(self):
        self.clear_cooke()
        self.redirect('signup')


#When users login or sign up, this page welcomes then and then redirects them
#Redirection is handled in the meta tag in welcome.html
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
        #Query that searches in Post for attributees isRoot and ancestor
        comments_query = Post.query(Post.isRoot == False,
                ancestor=blog_query.key).order(-Post.created)
        comments = comments_query.fetch(10)
        self.render("blogPost.html", blog_query = blog_query, comments = comments)

    def get(self):
        blog_post_id = int(self.request.get('blog_post_id', default_post_id))
        blog_query = Post.get_by_id(blog_post_id)

        if blog_query:
            self.render_front(blog_query)
        else:
            self.render_not_found()

    def post(self):
        if not self.check_cookie():
            self.redirect('/invalidCookie')

        username = self.request.cookies.get("username")
        content = self.request.get("content")

        blog_post_id = int(self.request.get('blog_post_id', default_post_id))
        blog_query = Post.get_by_id(blog_post_id)

        #Create Post child(this is a comment) on blog_query
        post_key = Post(parent = blog_query.key, author = username, content = content)
        post_key.put()

        self.render_front(blog_query)


class EditPostPage(Handler):

    def render_front(self, blog_query = "", error = ""):
        self.render("editPost.html", blog_query = blog_query, error = error)

    def get(self):
        if not self.check_cookie():
            self.redirect('/invalidCookie')

        blog_query = self.find_blog_query()

        if blog_query:
            if self.isOwner(blog_query.author):
                self.render_front(blog_query)
            else:
                self.render_front(blog_query, "You are not the owner")
        else:
            self.render_not_found()

    def post(self):
        if not self.check_cookie():
            self.redirect('/invalidCookie')

        blog_query = self.find_blog_query()

        if blog_query:
            if self.isOwner(blog_query.author):
                blog_query.title = self.request.get("title")
                blog_query.content = self.request.get("content")
                blog_query.put()
                self.render_front(blog_query)
            else:
                self.render_front(blog_query, "You are not the owner")
        else:
            self.render_not_found()


class DeletePostPage(Handler):

    def render_front(self, blog_query = "", error = ""):
        self.render("deletePost.html", blog_query = blog_query, error = error)

    def get(self):
        if not self.check_cookie():
            self.redirect('/invalidCookie')

        blog_query = self.find_blog_query()

        if blog_query:
            if self.isOwner(blog_query.author):
                self.render_front(blog_query)
            else:
                self.render_front(blog_query, "You are not the owner")
        else:
            self.render_not_found()

    def post(self):
        if not self.check_cookie():
            self.redirect('/invalidCookie')

        blog_query = self.find_blog_query()
        response = int(self.request.get('q1'))

        if blog_query:
            if self.isOwner(blog_query.author) and (response == 1):
                blog_query.key.delete()
                self.redirect("/")
            elif self.isOwner(blog_query.author) and (response == 0):
                self.render_front(blog_query, "Post remains intact!")
            else:
                self.render_front(blog_query, "You are not the owner")
        else:
            self.render_not_found()

class votePage(Handler):

    def decideValue(self, value):
        value = int(value)
        if value >= 1:
            value = 1
        else:
            value = -1
        return value

    def get(self):
        blog_query = self.find_blog_query()
        parent_id = self.request.get("parent")
        voter = self.request.cookies.get("username")
        value = self.request.get("value")

        if value:
            value = self.decideValue(value)

        if blog_query:
            vote_query = Vote.query(Vote.post == blog_query.key, Vote.user_id ==  voter).get()
            if vote_query:
                self.write(vote_query.value)
                if vote_query.value != value:
                    vote_query.value = value
                    #Mulitply by 2 to undo previous action
                    blog_query.likes += (2 * value)
            else:
                vote_query = Vote(post = blog_query.key, user_id = voter, value = value)
                blog_query.likes += value
            vote_query.put()
            blog_query.put()

            if parent_id:
                query_params = {'blog_post_id': parent_id}
            else:
                blog_query_id = blog_query.key.id()
                query_params = {'blog_post_id': blog_query_id}
            self.redirect('/blogPost?' + urllib.urlencode(query_params))

        self.render_not_found()


app = webapp2.WSGIApplication([('/', FrontPage),
                                ('/signup', SignUpPage),
                                ('/invalidCookie', InvalidCookiePage),
                                ('/login', LoginPage ),
                                ('/welcome', WelcomePage),
                                ('/logout', LogoutPage),
                                ('/createPost', CreatePostPage),
                                ('/blogPost', BlogPostPage),
                                ('/editPost', EditPostPage),
                                ('/deletePost', DeletePostPage),
                                ("/vote", votePage),

                                ],
                                debug=True)
