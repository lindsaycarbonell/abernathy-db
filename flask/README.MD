## Flask Merger
This application is solely for facilitating the merge between Editor & Publisher's database and our original database. The application is built in Flask with the connecting database in SQLite.

### Installation
- Start the virtual environment
  - `. venv_flask/bin/activate`
- Set your FLASK_APP variable
  - `export FLASK_APP=index.py`
- Run the application
  - `flask run`

### Design changes
- Make the state name at the top of home a dropdown menu, show state selection page only on start.
- Make color change happen on a "change color" selector right above "Back to top"
- Add an arrow beside "Back to top"
- Make ampersands show up correctly
- Add the "clear" command to the UI
- Have a giant arrow that points to the "Attempt merge" when you come to a new state
- Turn off the column switching on the index tables
- Change are/is for if there is 1 duplicate in the warning
- Fix alignment inside match form and make form title larger
- Have all button styles match


### Helpful Links

- https://stackoverflow.com/questions/20843085/url-for-is-not-defined-in-flask
- http://code.runnable.com/UhLMQLffO1YSAADK/handle-a-post-request-in-flask-for-python
- http://flask.pocoo.org/docs/0.10/quickstart/#variable-rules
- https://stackoverflow.com/questions/32019733/getting-value-from-select-tag-using-flask
- https://blog.syncano.io/intro-flask-pt-2-creating-writing-databases/

- https://github.com/GarenLiang/Flask/blob/2fa8ec7fcd55b275819a22ab9eee5b58fc0cb1ce/flask_prac/library/_12_database_app_with_join.py
