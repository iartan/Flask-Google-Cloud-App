# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_render_template]
# [START gae_python3_render_template]
import datetime
from flask import Flask, render_template, request
from google.auth.transport import requests
from google.cloud import datastore
import google.oauth2.id_token

firebase_request_adapter = requests.Request()


app = Flask(__name__)

datastore_client = datastore.Client()

my_tasks = {
            '1': {
                'title': 'New List',
            }
        }

def store_time(email, todo):
    entity = datastore.Entity(key=datastore_client.key('User', email, 'visit'))
    dt = datetime.datetime.now()
    entity.update({
        'timestamp': dt,
        'task': todo
    })

    datastore_client.put(entity)

def store_task(email, task, task_list_index):
    global my_tasks

    complete_key = datastore_client.key('to-do-list', email)
    db_task = datastore.Entity(key=complete_key)

    dict = my_tasks
    print(dict)

    dict[task_list_index].update({ str(len(dict[task_list_index])): task})
    print(len(dict[task_list_index]))
    db_task.update(
        dict
    )
    print(dict)
    datastore_client.put(db_task)

def store_task_list(email, name, color):
    global my_tasks

    complete_key = datastore_client.key('to-do-list', email)
    db_task = datastore.Entity(key=complete_key)

    dict = my_tasks
    print(dict)

    dict.update({ str(len(dict) + 1 ): { 'title': name, 'color': color }})

    db_task.update(
        dict
    )
    print(dict)
    datastore_client.put(db_task)

def initial_store(email=None, task=None):
    global my_tasks

    complete_key = datastore_client.key('to-do-list', email)
    task = datastore.Entity(key=complete_key)

    dict = my_tasks

    task.update(
        dict
    )

    datastore_client.put(task)

def fetch_tasks(email, limit):
    global my_tasks
    # ancestor = datastore_client.key('User', email)
    # query = datastore_client.query(ancestor=ancestor)
    # query.order = ['-timestamp']

    # times = query.fetch(limit=limit)
    key = datastore_client.key('to-do-list', email)
    my_tasks = datastore_client.get(key)

    # If there isn't any key for that email:
    try:
        print(dict(my_tasks))
        print(type(my_tasks))
        return dict(my_tasks)
    except:
        print('Probably no key...')
        my_tasks = {
            '1': {
                'title': 'New List',
            }
        }
        initial_store(email)
        return dict(my_tasks)

@app.route('/')
def root():
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    global my_tasks
    tasks_contents = None

    if id_token:
        try:
            # Verify the token against the Firebase Auth API. This example
            # verifies the token on each page load. For improved performance,
            # some applications may wish to cache results in an encrypted
            # session store (see for instance
            # http://flask.pocoo.org/docs/1.0/quickstart/#sessions).
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

            # store_time(claims['email'], datetime.datetime.now())
            my_tasks = fetch_tasks(claims['email'], 10)
            # tasks_contents = tasks['board_1']
            # tasks_contents = tasks_contents['2']
            # tasks_contents = tasks_contents['board_1']

        except ValueError as exc:
            # This will be raised if the token is expired or any other
            # verification checks fail.
            error_message = str(exc)

        # Record and fetch the recent times a logged-in user has accessed
        # the site. This is currently shared amongst all users, but will be
        # individualized in a following step.
        # store_time(datetime.datetime.now())
        # times = fetch_times(10)

        print('Ausloggen.')
        return render_template(
            'index.html',
            user_data=claims, error_message=error_message, tasks=my_tasks, tasks_contents=tasks_contents)

    else:
        return render_template(
            'index.html',
            user_data=claims, error_message=error_message)


@app.route('/', methods=['GET', 'POST'])
def action():
    global my_tasks

    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

            input = request.form.get('input')
            callback = request.form.get('callback')
            color = request.form.get('color')

            print(input)
            # print(type(input))
            print(callback)
            # print(type(callback))
            print(color)
            print(type(color))

            if input == '' or input == None:
                print('Input is empty.')
            elif callback == 'new_list':
                print('Neue Liste erstellen.')
                store_task_list(claims['email'], input, color)
            else:
                store_task(claims['email'], input, callback)
                print('Neuer Task.')
                pass

        except ValueError as exc:
            # This will be raised if the token is expired or any other
            # verification checks fail.
            error_message = str(exc)
            return render_template(
                'index.html',
                user_data=claims, error_message=error_message, tasks=my_tasks)

    return '', 204

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=4000, debug=True)
# [END gae_python3_render_template]
# [END gae_python38_render_template]
