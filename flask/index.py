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
        for idx, newspaper in enumerate(query_db('SELECT * FROM ep_2017 WHERE Streetaddressstate = ?', [this_state])):
            ep_papers[idx]['newspaper_name'] = newspaper['pub_companyName']
            ep_papers[idx]['city'] = newspaper['Streetaddresscity']
            ep_papers[idx]['county'] = newspaper['County']

        ## get counts
        db_total = len(state_papers)
        ep_total = len(ep_papers)
        # print('db_total: %s \n ep_total: %s' % (db_total, ep_total))

        # --- check to see if coming from /merge or /select ---
        # if merged_papers:
        #     return render_template('index.html', cssurl = css_url, states = states, state_papers=state_papers, ep_papers=ep_papers, state=state, db_total=db_total, ep_total=ep_total, merged_papers=merged_papers)
        # else:
        return render_template('index.html', cssurl = css_url, states = states, state_papers=state_papers, ep_papers=ep_papers, state=state, db_total=db_total, ep_total=ep_total)
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

@app.route('/merge/', methods=['POST', 'GET'])
def attempt_merge():
    this_state = request.args.get('state')
    state_str = [this_state][0].strip("[u'").strip("''")

    merged_papers = defaultdict(dict)
    for idx, newspaper in enumerate(query_db('SELECT t1.newspaper_name, t2.pub_companyName, t1.city, t2.Streetaddresscity FROM (SELECT * FROM newspaper WHERE state = "' + state_str + '") AS t1 INNER JOIN ep_2017 AS t2 ON (t1.newspaper_name = t2.pub_companyName OR "The " || trim(replace(t1.newspaper_name,"The","")) = t2.pub_companyName) AND (UPPER(t1.city) = UPPER(t2.Streetaddresscity)) ORDER BY t1.newspaper_name ASC')):
        # print newspaper['t1.newspaper_name']
        merged_papers[idx]['newspaper_name'] = newspaper['t1.newspaper_name']
        merged_papers[idx]['city'] = newspaper['t1.city']

    print urllib.urlencode(merged_papers)

    return render_template('merge.html', merged_papers=merged_papers)
    # return redirect(url_for('/', merged_papers))


if __name__=='__main__':
    app.run(debug=True)
