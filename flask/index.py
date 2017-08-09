from flask import Flask, url_for, request, g, redirect, flash, session
from flask import render_template
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
app = Flask(__name__)

app.secret_key = '8XGO8DVb65__2MTi5yssLX'

from collections import defaultdict

import sqlite3
DATABASE = 'abernathy.db'

with app.app_context():
    full_states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
        }

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

    def commit_db(query, args=(), one=False):
        con = sqlite3.connect("abernathy.db")
        cur = con.cursor()
        cur.execute(query, args)
        con.commit()
        con.close()

    states = query_db('SELECT state FROM newspaper GROUP BY state')


@app.route('/', methods=['GET', 'POST'])
def show_home():
    css_url = url_for('static', filename='style.css')
    if request.method == 'POST':
        state=request.form['state']
        return redirect(url_for('get_state_page', state=state))
    else:
        return render_template('selectstate.html', states=states, cssurl=css_url)

@app.route('/clear', methods=['GET', 'POST'])
def clear_merge_attempt():
        query_db('DROP VIEW IF EXISTS merge_attempt')
        flash('Merge attempt dropped!')
        return redirect(url_for('show_home'))

@app.route('/<state>/', methods=['POST', 'GET'])
def get_state_page(state):
    print 'GET STATE PAGE'
    css_url = url_for('static', filename='style.css')
    this_state=state
    is_duplicate=False
    num_of_dupl=0
    state_papers = defaultdict(dict)
    for idx, newspaper in enumerate(query_db('select * from newspaper where state = ?', [this_state])):
        state_papers[idx]['newspaper_id'] = newspaper['newspaper_id']
        state_papers[idx]['newspaper_name'] = newspaper['newspaper_name']
        state_papers[idx]['city'] = newspaper['city']



    ## get counts
    db_total = len(state_papers)


    try:
        query_db('SELECT 1 FROM merge_attempt LIMIT 1;')
        merge_exists = True
    except:
        merge_exists = False

    if merge_exists:
        merged_papers = defaultdict(dict)
        unmerged_papers = defaultdict(dict)
        unmerged_ep = defaultdict(dict)
        ep_papers = defaultdict(dict)

        # ... and from ep papers
        for idx, newspaper in enumerate(query_db('SELECT * FROM ep_2017 WHERE Streetaddressstate = ? AND ep_id NOT IN (SELECT ep_id FROM merge_attempt)', [this_state])):
            ep_papers[idx]['newspaper_name'] = newspaper['pub_companyName']
            ep_papers[idx]['city'] = newspaper['Streetaddresscity']

        ep_total = len(ep_papers)

        ## ...and from the merged_papers
        for idx, newspaper in enumerate(query_db('SELECT * FROM merge_attempt ORDER BY newspaper_name ASC')):
            # print newspaper['newspaper_name']
            merged_papers[idx]['newspaper_name'] = newspaper['newspaper_name']
            merged_papers[idx]['city'] = newspaper['city']

        for idx, newspaper in enumerate(query_db('SELECT newspaper_name, city FROM newspaper WHERE newspaper_name NOT IN (SELECT newspaper_name FROM merge_attempt) AND state = ?', [this_state])):
            # print newspaper['newspaper_name']
            unmerged_papers[idx]['newspaper_name'] = newspaper['newspaper_name']
            unmerged_papers[idx]['city'] = newspaper['city']

        # print this_state
        #
        # for idx, newspaper in enumerate(query_db('SELECT pub_companyName AS newspaper_name, Streetaddresscity AS city FROM ep_TN WHERE ep_id NOT IN (SELECT ep_id FROM merge_attempt)')):
        #     print 'running'
        #     print newspaper['ep_id']
        #     unmerged_ep[idx]['ep_id'] = newspaper['ep_id']
        #     unmerged_ep[idx]['newspaper_name'] = newspaper['newspaper_name']
        #     unmerged_ep[idx]['city'] = newspaper['city']


        unmerged_total = len(unmerged_papers)
        merged_total = len(merged_papers)
        if db_total-merged_total != unmerged_total:
            is_duplicate = True
            num_of_dupl = abs((db_total-merged_total)-unmerged_total)
        # ep_unmerged_total = len(unmerged_ep)

        # print unmerged_total

        return render_template('index.html', cssurl=css_url, states=states, state_papers=state_papers, ep_papers=ep_papers, state=state, db_total=db_total, ep_total=ep_total, merged_papers=merged_papers, merged_total=merged_total, unmerged_papers=unmerged_papers, unmerged_total=unmerged_total, is_duplicate=is_duplicate, num_of_dupl=num_of_dupl, full_state=full_states[state])
    else:
        return render_template('index.html', cssurl = css_url, states = states, state_papers=state_papers, state=state, db_total=db_total, full_state=full_states[state])




@app.route('/select/', methods=['POST', 'GET'])
def get_state():
    css_url = url_for('static', filename='style.css')
    query_db('DROP VIEW IF EXISTS merge_attempt')
    if request.method == 'POST':
        state=request.form['state']
        return redirect(url_for('/', state=state))
    else:
        return render_template('selectstate.html', states=states, cssurl=css_url)

@app.route('/update/', methods=['POST', 'GET'])
def update_db():
    state=request.args.get('state')
    css_url = url_for('static', filename='style.css')
    query_db('''CREATE TABLE IF NOT EXISTS overall_merge_changes (
    id integer PRIMARY KEY,
    state text,
    db_changed text,
    old_paper text,
    old_city text,
    column_changed text,
    changed_to text
    )''')
    if request.method == 'POST':
        db_newcity=request.form['inputDbSelCity']
        db_oldcity=request.form['oldDbCity']
        db_newpaper=request.form['inputDbSelPaper']
        db_oldpaper=request.form['oldDbPaper']

        ep_newcity=request.form['inputEpSelCity']
        ep_oldcity=request.form['oldEpCity']
        ep_newpaper=request.form['inputEpSelPaper']
        ep_oldpaper=request.form['oldEpPaper']

        # if db_oldpaper == ep_oldpaper:
        #     print 'we just need to update city...'
        #     print 'the city for ep was: ' + ep_oldcity
        #     print 'now for db it is: ' + ep_oldcity.title()
        #
        #     commit_db('UPDATE newspaper SET city = "%s" WHERE state = "%s" AND newspaper_name = "%s"' % (ep_oldcity.title(), state, db_oldpaper))
        #     commit_db('INSERT INTO overall_merge_changes (state, db_changed, old_paper, old_city, column_changed, changed_to) VALUES ("%s", "DB", "%s", "%s", "CITY", "%s")' % (state, db_oldpaper, db_oldcity, ep_oldcity.title()))

        if db_newcity != db_oldcity:
            print 'update city in db...'

            commit_db('UPDATE newspaper SET city = "%s" WHERE state = "%s" AND newspaper_name = "%s"' % (db_newcity, state, db_oldpaper))
            commit_db('INSERT INTO overall_merge_changes (state, db_changed, old_paper, old_city, column_changed, changed_to) VALUES ("%s", "DB", "%s", "%s", "CITY", "%s")' % (state, db_oldpaper, db_oldcity, db_newcity))

        if ep_newcity != ep_oldcity:
            print 'update city in ep...'

            commit_db('UPDATE ep_2017 SET Streetaddresscity = "%s" WHERE Streetaddressstate = "%s" AND pub_companyName = "%s"' % (ep_newcity, state, ep_oldpaper))
            commit_db('INSERT INTO overall_merge_changes (state, db_changed, old_paper, old_city, column_changed, changed_to) VALUES ("%s", "EP", "%s", "%s", "CITY", "%s")' % (state, ep_oldpaper, ep_oldcity, ep_newcity))

        if db_newpaper != db_oldpaper:
            print 'update paper in db...'

            commit_db('UPDATE newspaper SET newspaper_name = "%s" WHERE state = "%s" AND newspaper_name = "%s"' % (db_newpaper, state, db_oldpaper))
            commit_db('INSERT INTO overall_merge_changes (state, db_changed, old_paper, old_city, column_changed, changed_to) VALUES ("%s", "DB", "%s", "%s", "PAPER", "%s")' % (state, db_oldpaper, db_oldcity, db_newpaper))

        if ep_newpaper != ep_oldpaper:
            print 'update paper in ep...'

            commit_db('UPDATE ep_2017 SET pub_companyName = "%s" WHERE Streetaddressstate = "%s" AND pub_companyName = "%s"' % (ep_newpaper, state, ep_oldpaper))
            commit_db('INSERT INTO overall_merge_changes (state, db_changed, old_paper, old_city, column_changed, changed_to) VALUES ("%s", "EP", "%s", "%s", "PAPER", "%s")' % (state, ep_oldpaper, ep_oldcity, ep_newpaper))

        return redirect(url_for('get_state_page', state=state))

    else:
        return render_template('update.html', state=state, cssurl=css_url)

@app.route('/<state>/merge/', methods=['POST', 'GET'])
def attempt_merge(state):

    # print 'ATTEMPT MERGE'

    this_state=state
    # print this_state
    state_str = [this_state][0].strip("[u'").strip("''")

    query_db('DROP VIEW IF EXISTS merge_attempt')
    # query_db('DROP VIEW IF EXISTS ep_%s' % (state_str))

    query_db('''CREATE VIEW IF NOT EXISTS ep_%s AS
    SELECT * FROM ep_2017
    WHERE Streetaddressstate = "%s"
    ''' % (state_str, state_str))

    # print query_db('SELECT * FROM ep_%s' % (state_str))

    query_db('''CREATE VIEW IF NOT EXISTS merge_attempt AS SELECT t2.ep_id AS ep_id, t1.newspaper_id AS db_id, t1.newspaper_name AS newspaper_name, t1.city AS city
    FROM newspaper_2017 AS t1
    INNER JOIN ep_%s AS t2
    ON ( t1.newspaper_name = t2.pub_companyName
    OR "The " || trim(replace(t1.newspaper_name,'The','')) = t2.pub_companyName
    OR REPLACE(t1.newspaper_name,'-',' ') = REPLACE(t2.pub_companyName,'-',' ')
    OR trim(replace(t1.newspaper_name,'The','')) = t2.pub_companyName)
    AND (trim(REPLACE(UPPER(t1.city),'CITY','')) = trim(REPLACE(UPPER(t2.Streetaddresscity),'CITY','')))
    WHERE t1.state = "%s"
    ORDER BY newspaper_name ASC''' % (state_str, state_str))


    return redirect(url_for('get_state_page', state=state))

@app.route('/<state>/show_merge/', methods=['POST', 'GET'])
def show_merge(state):
    this_state=state
    state_str = [this_state][0].strip("[u'").strip("''")

    query_db('DROP VIEW IF EXISTS final_merge')

    # query_db('DROP VIEW IF EXISTS ep_%s' % (state_str))

    query_db('''CREATE VIEW IF NOT EXISTS ep_%s AS
    SELECT * FROM ep_2017
    WHERE Streetaddressstate = "%s"
    ''' % (state_str, state_str))

    query_db('''
    CREATE VIEW final_merge AS
    SELECT state, newspaper_id, newspaper_name, frequency, AvgPaidCirc AS ep_paid_circ, total_circulation AS db_total_circ, AvgFreeCirc AS ep_free_circ,
    ABS((CAST(AvgPaidCirc AS INTEGER) + CAST(AvgFreeCirc AS INTEGER)) - CAST(REPLACE(total_circulation,',','') AS INTEGER)) AS circDiff,
    AuditBy AS ep_audit_by, AuditDate AS ep_audit_date, ParentCompany AS ep_owner,
    t2.pub_companyName AS ep_newspaper_name,
    t1.city AS city, t1.county AS county FROM newspaper_2017 AS t1
    LEFT OUTER JOIN ep_%s AS t2 ON
    ( t1.newspaper_name = t2.pub_companyName
    OR "The " || trim(replace(t1.newspaper_name,'The','')) = t2.pub_companyName
    OR  REPLACE(t1.newspaper_name,"-"," ") = REPLACE(t2.pub_companyName,"-"," ")
    OR trim(replace(t1.newspaper_name,'The','')) = t2.pub_companyName ) AND
    ( trim(REPLACE(UPPER(t1.city),"CITY","")) = trim(REPLACE(UPPER(t2.Streetaddresscity),"CITY",""))
    )
    WHERE t1.state = "%s"
    ORDER BY newspaper_name ASC
    ''' % (state_str, state_str))


    all_merged_papers = defaultdict(dict)
    ## ...and from the merged_papers
    for idx, newspaper in enumerate(query_db('''
    SELECT t1.newspaper_id AS newspaper_id, t1.newspaper_name AS newspaper_name, t1.frequency AS db_frequency,
    t1.ep_paid_circ AS ep_paid_circ, t2.db_total_circ AS db_total_circ, t1.ep_free_circ AS ep_free_circ,
    t1.circDiff AS circDiff, t2.freq_2004 AS freq_2004, t2.total_circulation_2004 AS total_circ_2004,
    t2.owner_name AS db_owner, t1.ep_owner AS ep_owner, t2.city AS city, t2.county AS county, t1.ep_audit_by
    AS ep_audit_by, t1.ep_audit_date AS ep_audit_date, t1.ep_newspaper_name AS ep_newspaper_name FROM final_merge AS t1
    LEFT JOIN all_2017 AS t2 ON t2.newspaper_id = t1.newspaper_id
    ''')):
        # print newspaper['newspaper_id']
        all_merged_papers[idx]['newspaper_id'] = newspaper['newspaper_id']
        all_merged_papers[idx]['newspaper_name'] = newspaper['newspaper_name']
        all_merged_papers[idx]['db_frequency'] = newspaper['db_frequency']
        all_merged_papers[idx]['ep_paid_circ'] = newspaper['ep_paid_circ']
        all_merged_papers[idx]['db_total_circ'] = newspaper['db_total_circ']
        all_merged_papers[idx]['ep_free_circ'] = newspaper['ep_free_circ']
        all_merged_papers[idx]['circDiff'] = newspaper['circDiff']
        all_merged_papers[idx]['freq_2004'] = newspaper['freq_2004']
        all_merged_papers[idx]['total_circ_2004'] = newspaper['total_circ_2004']
        all_merged_papers[idx]['db_owner'] = newspaper['db_owner']
        all_merged_papers[idx]['ep_owner'] = newspaper['ep_owner']
        all_merged_papers[idx]['city'] = newspaper['city']
        all_merged_papers[idx]['county'] = newspaper['county']
        all_merged_papers[idx]['ep_audit_by'] = newspaper['ep_audit_by']
        all_merged_papers[idx]['ep_audit_date'] = newspaper['ep_audit_date']
        all_merged_papers[idx]['ep_newspaper_name'] = newspaper['ep_newspaper_name']

    # print all_merged_papers[4]

    return render_template('finaltable.html', state=state, all_merged_papers=all_merged_papers)




if __name__=='__main__':
    app.run(debug=True)
