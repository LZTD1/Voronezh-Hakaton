import asyncio
import datetime

from flask import Flask, render_template, request
# from hypercorn.asyncio import serve
from database import Database

app = Flask(__name__, template_folder="template")
db = Database("localhost", "5432", "postgres", "123321", "fsb_database")

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
async def do_login():

    username = request.form['username']
    password = request.form['password']
    await db.connect()
    result = await db.authenticate_user(username, password)
    await db.disconnect()
    if result:
        return 'Authentication successful'
    else:
        return 'Authentication failed'

@app.route('/register', methods=['POST'])
async def do_register():

    username = request.form['login']
    password = request.form['pwd']
    await db.connect()
    authenticated = await db.register_user(username, password, datetime.datetime.now(),"first_name","last_name","petronymic","[]","[]")
    await db.disconnect()
    return "popa"

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
    # serve(app, bind="localhost:5000")
