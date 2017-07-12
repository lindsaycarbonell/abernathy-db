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


    for state in states:
        print state


    # get a table
    this_state = 'DC'
    DC_papers = defaultdict(dict)

    for idx, newspaper in enumerate(query_db('select * from newspaper where state = ?', [this_state])):

        DC_papers[idx]['newspaper_id'] = newspaper['newspaper_id']
        DC_papers[idx]['newspaper_name'] = newspaper['newspaper_name']
        DC_papers[idx]['city'] = newspaper['city']
        DC_papers[idx]['county'] = newspaper['county']


    # print DC_papers
    #
    # for k,v in DC_papers.items():
    #     print(k)
    #     for key, value in v.items():
    #         print k[0][value]

@app.route('/', methods=['GET', 'POST'])
def form():
    css_url = url_for('static', filename='style.css')
    if request.method == 'POST':
        state=request.form['state']
        return render_template('index.html', cssurl = css_url, states = states, dcpapers = DC_papers, state=state)
    else:
        return render_template('index.html', cssurl = css_url, states = states, dcpapers = DC_papers, state=None)


@app.route('/select/', methods=['POST', 'GET'])
def get_state():
    if request.method == 'POST':
        state=request.form['state']
        css_url = url_for('static', filename='style.css')
        return redirect(url_for('/', state=state))
    else:
        return render_template('selectstate.html', states=states)


# @app.route('/', methods=['GET', 'POST'])
# def show_index():
#     if request.method == 'POST':
#         return redirect(url_for('state', state=request.form['state']))
#     else:
#         css_url = url_for('static', filename='style.css')
#         return render_template('index.html', cssurl = css_url, states = states, dcpapers = DC_papers)
#
# @app.route('/select_state')
# def form():
#     return render_template('selectstate.html', states=states)
#
# @app.route('/state/<state>', methods=['GET', 'POST'])
# def state_select(state=None):
#     if request.method == 'POST':
#         return redirect(url_for('state',state=state))
#     else:
#         return render_template('index.html', cssurl = css_url, states = states, dcpapers = DC_papers, state=state)

# @app.route('/state_select', methods=['GET','POST'])
# def state_select():
#     select = request.form.get('state_select')
#     return(str(select))

if __name__=='__main__':
    app.run(debug=True)
