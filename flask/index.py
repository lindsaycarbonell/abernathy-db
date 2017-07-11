# http://flask.pocoo.org/docs/0.12/quickstart/
from flask import Flask, url_for, request, g
from flask import render_template
app = Flask(__name__)

from collections import defaultdict

import sqlite3
DATABASE = 'abernathy.db'

with app.app_context():

    def get_db():
        db = getattr(g, "_database", None)
        if db is None:
            db = g._database = sqlite3.connect(DATABASE)
            db.row_factory = sqlite3.Row
        return db

    @app.teardown_appcontext
    def close_connection(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

    # query function to get cursor, execute and fetch results
    def query_db(query, args=(), one=False):
        cur = get_db().execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv

    this_state = 'DC'
    DC_papers = defaultdict(dict)

    for idx, newspaper in enumerate(query_db('select * from newspaper where state = ?', [this_state])):

        DC_papers[idx]['newspaper_id'] = newspaper['newspaper_id']
        DC_papers[idx]['newspaper_name'] = newspaper['newspaper_name']
        DC_papers[idx]['city'] = newspaper['city']
        DC_papers[idx]['county'] = newspaper['county']

    for k,v in DC_papers.items():
        print(v)

@app.route('/')
@app.route('/index/<name>')
def index(name=None):
    css_url = url_for('static', filename='style.css')
    return render_template('index.html', name=name, cssurl = css_url, dcpapers = DC_papers)
