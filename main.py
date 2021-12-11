from flask import Flask, jsonify, request, make_response, redirect
import jwt
import datetime
from functools import wraps
from flask_swagger_ui import get_swaggerui_blueprint
from mysql.connector import cursor
import mysql.connector

import json

# from routes import request_api
app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'


# SWAGGER_URL = '/swagger'
# API_URL = '/static/swagger.json'
# SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
#     SWAGGER_URL,
#     API_URL,
#     config={
#         'app_name': "Seans-Python-Flask-REST-Boilerplate"
#     }
# )
# app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


# Token Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message': 'Token is missing'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated


# Unprotected Route and function
@app.route('/')
def index():
    return redirect('http://127.0.0.1:5000/login')


@app.route('/data', methods=['GET'])
def house():
    vrbo_data = []

    db_connector = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="hotel"
    )

    title = request.args.get('title')
    bedroom = request.args.get('bedroom')
    sleep = request.args.get('sleep')
    bathroom = request.args.get('bathroom')
    price = request.args.get('price')
    location = request.args.get('location')

    cursor = db_connector.cursor()

    sql = "SELECT * FROM vacation_rentals WHERE "
    valudata = 0

    if (title != None):
        if sql == 'SELECT * FROM vacation_rentals WHERE ':
            sql = sql + "title=" + f"'{title}'"
        else:
            sql = sql + "AND title=" + f"' {title}'"

    if (location != None):
        if sql == 'SELECT * FROM vacation_rentals WHERE ':
            sql = sql + "location=" + f"'{location}'"
        else:
            sql = sql + "AND location=" + f"'{location}'"
    if (bedroom != None):
        if sql == 'SELECT * FROM vacation_rentals WHERE ':
            sql = sql + "bedroom=" + f"'{bedroom}'"
        else:
            sql = sql + "AND bedroom>=" + f"'{bedroom}'"
    if (bathroom != None):
        if sql == 'SELECT * FROM vacation_rentals WHERE ':
            sql = sql + "bathroom>=" + f"'{bathroom}'"
        else:
            sql = sql + "AND bathroom>=" + f"'{bathroom}'"
    if (sleep != None):
        if sql == 'SELECT * FROM vacation_rentals WHERE ':
            sql = sql + "sleep>=" + f"'{sleep}'"
        else:
            sql = sql + "AND sleep>=" + f"'{sleep}'"
    if (price != None):
        if sql != 'SELECT * FROM vacation_rentals WHERE ':
            sql = sql + "AND price>=" + f"'${price}'"
        else:
            sql = sql + "price>=" + f"'${price}'"

    query = sql
    print(query)
    cursor.execute(query)

    results = cursor.fetchall()

    for x in results:
        data = {
            "id": x[0],
            "Title": x[1],
            "Sleeps": x[2],
            "Bedrooms": x[3],
            "Bathrooms": x[4],
            "Images": {
                "Image1": x[5][1:-1],
                "Image2": x[6][1:-1],
                "Image3": x[7][1:-1],
            },
            "Price": x[8],
            "Location": x[9],
        }
        vrbo_data.append(data)
    vrbo_data.sort(key=lambda x: x["Price"])
    houseJson = json.dumps(vrbo_data, indent=4)
    print(houseJson)
    return houseJson


# Protected Route and function
@app.route('/protected')
@token_required
def protected():
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.json'
    SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Vrbo Hotel Data"
        }
    )
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
    return redirect("http://127.0.0.1:5000/swagger", code=302)


# Login Route and function
@app.route('/login')
def login():
    auth = request.authorization

    if auth and auth.password == '1234':
        token = jwt.encode({'user': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=500)},
                           app.config['SECRET_KEY'])
        return jsonify({'token': token})

    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm:"Login Required"'})


if __name__ == "__main__":
    app.run(debug=False)
