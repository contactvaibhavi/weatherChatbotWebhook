
from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response


import psycopg2
import urllib.parse as urlparse
import os

from pprint import pprint

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    #print("Request:")
    #print(json.dumps(req, indent=4))

    #res = processRequest(req)
    #res = json.dumps(res, indent=4)
    #print("yahaan")
    #r = make_response(res)

    r = db_simul(req)
    #r = {
    #"speech" : "VERY GOOD!",
    #"displayText" : "VERY VERY GOOD",
    #"source": "apiai-weather-webhook-sample"
    #}
    pprint(r)
    r.headers['Content-Type'] = 'application/json'

    return r

def db_simul(req):
    url = urlparse.urlparse(os.environ['DATABASE_URL'])
    dbname = url.path[1:]
    user = url.username
    password = url.password
    host = url.hostname
    port = url.port
    conn = psycopg2.connect(
    dbname = dbname,
    user = user,
    password = password,
    host = host,
    port = port
    )
    
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    tablename = "Users"
    cur.execute("CREATE TABLE Users(u_id integer, u_name varchar(20), u_email varchar(20), u_description text) ;")
    cur.execute("INSERT INTO Users VALUES (21, 'Vaibhavi', 'vaibhavisingh2402@gmail.com', 'She's awesome!') ;")
    cur.execute("SELECT * FROM Users;")

    rows = cur.fetchall()

    d    = dict()
    ans  = str()
    i=0

    for row in rows:
        d = dict(
            {
            'user' : str(row[1]),
            'tweet': str(row[2])
            }
            )
        if i == 0:
            ans = '{ ' + json.dumps(d)
        elif i > 0:
            ans += ', ' + json.dumps(d)
        
        i += 1

    ans += ' }'
    pprint(ans)

    cur.close()
    conn.close()

    return {
    "speech" : "VERY GOOD!",
    "displayText" : "VERY VERY GOOD",
    "source": "apiai-weather-webhook-sample"
    }

def processRequest(req):
    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today the weather in " + location.get('city') + ": " + condition.get('text') + \
             ", And the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
    "speech": speech,
    "displayText": speech,
        # "data": data,
        # "contextOut": [],
    "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
