# Item Catalog App

## About:
This project is for udacity FSND Course for RESTful web application using Flask framework and SQL database. Authentication is provided by AOuth2 for implementing Google account.

## Pre-requisites:
1. Python
2. HTML
3. CSS
4. Vagrant
5. Virtual Box

## How to Install
1. Install Vagrant & VirtualBox
2. Clone the Udacity Vagrantfile
3. Go to Vagrant directory and either clone this repo or download and place zip here
4. Launch the Vagrant VM (vagrant up)
5. Log into Vagrant VM (vagrant ssh)
6. Navigate to cd/vagrant as instructed in terminal
7. The app imports requests which is not on this vm. Run sudo pip install requests
8. Setup application database python /catalog/database_setup.py
9. Setup database python /catalog/lotsofcatalogs.py
10. Run application using python /catalog/project.py
11. Access the application locally using http://localhost:5000

## Using Google Login
To get the Google login working there are a few additional steps:

1. Go to Google Dev Console
2. Sign up or Login if prompted
3. Go to Credentials
4. Select Create Crendentials > OAuth Client ID
5. Select Web application
6. Enter name 'Catalog'
7. Authorized JavaScript origins = 'http://localhost:5000'
8. Authorized redirect URIs='http://localhost:5000/'
9. Select Create
10. Copy the Client ID and paste it into the data-clientid in login.html
11. On the Dev Console Select Download JSON
12. Rename JSON file to client_secrets.json
13. Place JSON file in item-catalog directory that you cloned from here
14. Run application using python /catalog/project.py

## JSON Endpoints
The following are open to the public:

1. Catalog JSON: /catalog/JSON - Displays the whole catalog. Categories and all items.

2. Category Items JSON: /catalog/<path:category_name>/items/JSON - Displays items for a specific category