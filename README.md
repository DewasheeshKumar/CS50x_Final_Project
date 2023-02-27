# myLedger

#### Made by [Chittesh1999](https://github.com/Chittesh1999)

#### Video Demo: https://youtu.be/x36GepEcecs

### Description:
myLedger is a webapp based on Flask and SQL to help various communities, clubs, corporates, startups or for personal use to keep track of various funds they have as well as their spendings on various stuffs given the support for various currency in available world for the people who have different account in different countries and the value to the balance in those accounts is shown with respect to USD in the web app with a live currency exchange rate API.

### Implementaion:
Flask is used as an base for coding this web application using various libraries as required while making of this an addition helpers.py is included for few extra funtions which were used for the ease of making this web app. The api provided by https://openexchangerates.org was used to show the currency rates and value of a particular account in USD

### Setup:
Intall various libraries required by:
> `pip install requirements.txt`

Get an API_KEY from https://openexchangerates.org
Next Export the API_KEY by:
> `export API_KEY=[your key]`

cd into the directory of webapp
Run
> `flask run` 

Follow URL from terminal

### Working:
After following the URL the user ends up in the login page if user doesn't have an an account they are supposed to make one by using register from the navbar after registering the user is redirected to login page from where they are supposed to login and end up in index page which contains instructions and various routes to different funtions of webapp

- `/` : This route leads to index of the Webapp
- `/login`: This route leads to the login page of the Webapp
- `/logout`: This route logouts the user from the Webapp
- `/register`: This route leads to the page for registering a user
- `/password`: This route leads to the page which is used for changing password of a user
- `/accounts`: This route leads user to the page which shows the table of various accounts with the balance, worth in USD and status which the user has added 
- `/transactions`: This route leads user to the page which shows the table of all payments done account added, funds transfered and at which time
- `/payment`: This route leads user to the form with which user can add the payments they have done from the account
- `/new`: This route leads user to the form through which user can add various accounts they want to track 
- `/funds`: This route leads user to the form through which user can add funds they have been getting in there accoounts to change status of account from blocked, inactive to active by adding 0 amount of equivalent currency of account using Add Funds

#### SQL queries used to create tables:

` CREATE TABLE users (
id INTEGER,
username TEXT NOT NULL,
hash TEXT NOT NULL,
worth NUMERIC NOT NULL DEFAULT 0.00,
PRIMARY KEY(id)); `
 
` CREATE UNIQUE INDEX username ON users (username); `

` CREATE TABLE accounts (
id INTEGER NOT NULL,
account_id INTEGER NOT NULL,
bank TEXT NOT NULL,
currency TEXT NOT NULL,
balance NUMERIC NOT NULL DEFAULT 0.00,
status TEXT NOT NULL,
PRIMARY KEY(id),
FOREIGN KEY(account_id) REFERENCES users(id));`

` CREATE TABLE transactions (
id INTEGER NOT NULL,
transaction_id INTEGER NOT NULL,
title TEXT NOT NULL,
amount NUMERIC NOT NULL,
currency TEXT NOT NULL,
bank TEXT NOT
time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY(id),
FOREIGN KEY(transaction_id) REFERENCES users(id));`