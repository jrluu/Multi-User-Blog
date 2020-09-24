# Multi User Blog

## Description

A live preview of this code is available [here](http://jrluudevs.com)

In this project, I created a website that allows you to register for an account, post a blog, comment on blog posts, and upvote/downvote them.

In order to create this website, I took advantage of Google Cloud app engine, which allows its users to rapidly deploy scalable web applications and mobile backends. To store the users and blog posts, I used Google's Cloud storage, a NoSQL database, because Google Cloud can easily add more nodes and automatically load balance stress between the nodes, allowing me to scale up as the userbase grows. To ensure that a user can stay signed into the blog, I implemented a session cookie that contains the username and the password, which is securely hashed to slow down a rainbow table attack.

In terms of the file structure of this code. All of the Python code is in the first directory and they are all compiled. The file, *blog.py*, contains all of the routing information. The folder, FrontEnd, contains the bootstrap files so I would not look there. The folder, *templates*, contain all of the HTML files. In the HTML files, I removed all of the spaces and returns to save bandwidth when sending it to the customer. Please look at the *template/assets* for the human readable format.

## Requirements
You must have the following installed  

* [Google Cloud](https://cloud.google.com/)   
* [Python 2.7](https://www.python.org/download/releases/2.7/)

## Navigating the directory
* FrontEnd/assets - Contains the css, js, and sass files  
* templates/assets - Contains the HTML files
* ./ - Contains python files, app.yaml, and index.yaml

## How to run locally
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


## How to develop
1. Install Grunt if you have not already  
`$ npm install -g grunt-cli`
2. Install Grunt Plugins  
`$ npm install`
3. Type in command to automatically optimize files  
`$ grunt watch`

## Possible Errors
1. NeedIndexError
 *  When the application is starting, [Datastore] (https://console.cloud.google.com/datastore/indexes?src=ac&project=iconic-computer-148708) needs to time to read the index.yaml file and load the predefined indexes
 * Another reason that you may get this error is if you did not deploy correctly. You MUST include the index.yaml file

For more information on indexing, see [this](https://cloud.google.com/appengine/docs/python/config/indexconfig)

## Technologies Used  
* [Google Cloud](https://cloud.google.com/)   
* [Google Cloud Storage(NoSQL)](https://cloud.google.com/storage/)  
* [Python 2.7] (https://www.python.org/download/releases/2.7/)
* [Jinja2](http://jinja.pocoo.org/docs/dev/)
* Hash Encryption
* Cookies

## For more information
Feel free contact me at jrluu@ucdavis.edu
