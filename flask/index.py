# http://flask.pocoo.org/docs/0.12/quickstart/
from flask import Flask, url_for, request, g, redirect, flash, session
from flask import render_template
app = Flask(__name__)

app.secret_key = '8XGO8DVb65__2MTi5yssLX'

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
def show_home():
    if request.method == 'POST':
        state=request.form['state']
        css_url = url_for('static', filename='style.css')
        return redirect(url_for('get_state_page', state=state))
    else:
        return render_template('selectstate.html', states=states)

@app.route('/clear', methods=['GET', 'POST'])
def clear_merge_attempt():
        query_db('DROP TABLE IF EXISTS merge_attempt')
        flash('Merge attempt dropped!')
        return redirect(url_for('show_home'))

@app.route('/<state>/', methods=['POST', 'GET'])
def get_state_page(state):
    css_url = url_for('static', filename='style.css')
    this_state=state
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

    try:
        query_db('SELECT 1 FROM merge_attempt LIMIT 1;')
        merge_exists = True
    except:
        merge_exists = False

    if merge_exists:
        merged_papers = defaultdict(dict)
        ## ...and from the merged_papers
        for idx, newspaper in enumerate(query_db('SELECT * FROM merge_attempt ORDER BY newspaper_name ASC')):
            merged_papers[idx]['newspaper_name'] = newspaper['newspaper_name']
            merged_papers[idx]['city'] = newspaper['city']

        merge_total = len(merged_papers)

        # for idx,newspaper in enumerate(query_db('SELECT t1.newspaper_name, pub_companyName, city, Streetaddresscity FROM merge_attempt')):
        #     print(newspaper['newspaper_name'])

        return render_template('index.html', cssurl = css_url, states = states, state_papers=state_papers, ep_papers=ep_papers, state=state, db_total=db_total, ep_total=ep_total, merged_papers=merged_papers, merge_total=merge_total)
    else:
        return render_template('index.html', cssurl = css_url, states = states, state_papers=state_papers, ep_papers=ep_papers, state=state, db_total=db_total, ep_total=ep_total)




@app.route('/select/', methods=['POST', 'GET'])
def get_state():
    if request.method == 'POST':
        state=request.form['state']
        css_url = url_for('static', filename='style.css')
        return redirect(url_for('/', state=state))
    else:
        return render_template('selectstate.html', states=states)

@app.route('/<state>/merge/', methods=['POST', 'GET'])
def attempt_merge(state):
    # this_state = request.args.get('state')
    this_state=state
    state_str = [this_state][0].strip("[u'").strip("''")

    query_db('DROP TABLE IF EXISTS merge_attempt')
    flash('Old merge table dropped!')
    query_db('CREATE TABLE merge_attempt AS SELECT t1.newspaper_name AS newspaper_name, t1.city AS city FROM (SELECT * FROM newspaper WHERE state = "' + state_str + '") AS t1 INNER JOIN ep_2017 AS t2 ON (t1.newspaper_name = t2.pub_companyName OR "The " || trim(replace(t1.newspaper_name,"The","")) = t2.pub_companyName) AND (UPPER(t1.city) = UPPER(t2.Streetaddresscity)) ORDER BY t1.newspaper_name ASC')
    flash('Merge table created!')
    return redirect(url_for('get_state_page', state=state))

    # merged_papers = defaultdict(dict)
    # for idx, newspaper in enumerate(query_db('SELECT t1.newspaper_name, t2.pub_companyName, t1.city, t2.Streetaddresscity FROM (SELECT * FROM newspaper WHERE state = "' + state_str + '") AS t1 INNER JOIN ep_2017 AS t2 ON (t1.newspaper_name = t2.pub_companyName OR "The " || trim(replace(t1.newspaper_name,"The","")) = t2.pub_companyName) AND (UPPER(t1.city) = UPPER(t2.Streetaddresscity)) ORDER BY t1.newspaper_name ASC')):
    #     merged_papers[idx]['newspaper_name'] = newspaper['t1.newspaper_name']
    #     merged_papers[idx]['city'] = newspaper['t1.city']
    #
    # return render_template('merge.html', merged_papers=merged_papers)


if __name__=='__main__':
    app.run(debug=True)
