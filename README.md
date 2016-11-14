#Multi User Blog

##Description

In this project, I created a website that allows you to register for an account,
 post a blog, comment on blog posts, and upvote/downvote them.

In order to create this website, I took advantage of Google Cloud app engine, which allows its users to rapidly deploy scalable web applications and mobile backends. To store the users and blog posts, I used Google's Cloud storage, a NoSQL database, because Google Cloud can easily add more nodes and automatically load balance stress between the nodes, allowing me to scale up as the userbase grows. To ensure that a user can stay signed into the blog, I implemented a session cookie that contains the username and the password, which is securely hashed to slow down a rainbow table attack.

##Requirements
You must have the following installed  

* [Google Cloud](https://cloud.google.com/)   
* [Python 2.7](https://www.python.org/download/releases/2.7/)

##How to run locally
1. Download the files
`$ git clone https://github.com/jrluu/Nanodegree.git `
2. Change to that directory
 `$ cd path/to/MultiUserBlog`
3. Run the appserver
`$ dev.appserver.py .``


## How to Deploy
1. Run it locally first to generate index.yaml and app.yaml (see instructions above)
2. Deploy it using gcloud
`$ gcloud app deploy app.yaml index.yaml`
3. View it on your local browser  
`$ gcloud app browse`

##Possible Errors
1. NeedIndexError
 *  When the application is starting, [Datastore] (https://console.cloud.google.com/datastore/indexes?src=ac&project=iconic-computer-148708) needs to time to read the index.yaml file and load the predefined indexes
 * Another reason that you may get this error is if you did not deploy correctly. You MUST include the index.yaml file

For more information on indexing, see [this](https://cloud.google.com/appengine/docs/python/config/indexconfig)

##Technologies Used  
* [Google Cloud](https://cloud.google.com/)   
* [Google Cloud Storage(NoSQL)](https://cloud.google.com/storage/)  
* [Python 2.7] (https://www.python.org/download/releases/2.7/)
* [Jinja2](http://jinja.pocoo.org/docs/dev/)
* Hash Encryption
* Cookies

##For more information
Please contact me at jrluu@ucdavis.edu
