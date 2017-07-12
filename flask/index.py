# http://flask.pocoo.org/docs/0.12/quickstart/
from flask import Flask, url_for, request, g, redirect
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

    states = query_db('SELECT state FROM newspaper GROUP BY state')

    ## Grab a state from EP in a tuple
    ep_papers = defaultdict(dict)
    ex_state = 'CT'
    address = 'Streetaddressstate'
    con = sqlite3.connect('abernathy.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM ep_2017 WHERE Streetaddressstate = ?', [ex_state])
    # print cur.fetchall()
    con.close()


@app.route('/', methods=['GET', 'POST'])
def form():
    css_url = url_for('static', filename='style.css')
    if request.method == 'POST':
        state=request.form['state']
        ## get DB state data needed to populate table
        this_state=request.form['state']
        state_papers = defaultdict(dict)
        for idx, newspaper in enumerate(query_db('select * from newspaper where state = ?', [this_state])):
            state_papers[idx]['newspaper_id'] = newspaper['newspaper_id']
            state_papers[idx]['newspaper_name'] = newspaper['newspaper_name']
            state_papers[idx]['city'] = newspaper['city']
            state_papers[idx]['county'] = newspaper['county']
        ## ...and get it from EP too
        ep_papers = defaultdict(dict)
        for idx, newspaper in enumerate(query_db('SELECT * FROM ep_2017 WHERE Streetaddressstate = ?', [ex_state])):
            ep_papers[idx]['newspaper_name'] = newspaper['pub_companyName']
            ep_papers[idx]['city'] = newspaper['Streetaddresscity']
            ep_papers[idx]['county'] = newspaper['County']
        return render_template('index.html', cssurl = css_url, states = states, state_papers=state_papers, ep_papers=ep_papers, state=state)
    else:
        return render_template('index.html', cssurl = css_url, states = states, state=None)


@app.route('/select/', methods=['POST', 'GET'])
def get_state():
    if request.method == 'POST':
        state=request.form['state']
        css_url = url_for('static', filename='style.css')
        return redirect(url_for('/', state=state))
    else:
        return render_template('selectstate.html', states=states)


if __name__=='__main__':
    app.run(debug=True)
