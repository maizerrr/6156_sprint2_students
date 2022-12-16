from flask import Flask, Response, request
from datetime import datetime
from flask_cors import CORS
import json
import sys
import pymysql
import os

# Initial DB connection
rds_host  = "sprint1studentsdb6156.cq0pqafrrlui.us-east-1.rds.amazonaws.com"
name = os.environ['db_username']
password = os.environ['db_password']
db_name = os.environ['db_name']


try:
    conn = pymysql.connect(host=rds_host, user=name, passwd=password, db=db_name, connect_timeout=20)
    print("SUCCESS: Connection to RDS MySQL instance succeeded.")
except pymysql.MySQLError as e:
    print("ERROR: Unexpected error: Could not connect to MySQL instance.")
    print(e)
    sys.exit()



# Create the Flask application object.
application = app = Flask(__name__)

CORS(app)


@app.get("/")
def get_health():
    t = str(datetime.now())
    msg = {
        "name": "E6156-sprint2-students",
        "health": "Good",
        "at time": t
    }
    return Response(json.dumps(msg), status=200, content_type="application/json")


# Define all routes mentioned in api readme
@app.route("/students", methods=["GET"])
def all_students():
    response = []
    conn.ping()
    with conn.cursor() as cur:
        cur.execute("SELECT studentID FROM Students")
        for row in cur:
            response.append(row)
    conn.commit()
    response = {
        'body': list( map(str, response) )
    }
    print("SUCCESS: {} item(s) retrieved from DB".format(len(response)))
    return Response(json.dumps(response), status=200, content_type="application/json")


@app.route("/students/<sid>", methods=["GET", "POST", "DELETE"])
def one_student(sid):
    if request.method == "GET":
        return get_one_student(sid)
    elif request.method == "POST":
        return insert_one_student(sid, request.form)
    elif request.method == "DELETE":
        return delete_one_student(sid)
    else:
        response = { 'body': "Request method {} not allowed".format(request.method) }
        return Response(json.dumps(response), status=500, content_type="application/json")

def get_one_student(sid):
    sql = "SELECT * FROM Students WHERE studentID = %s"
    response = None
    conn.ping()
    with conn.cursor() as cur:
        cur.execute(sql, (sid,))
        for row in cur:
            response = str(row)
            break
    conn.commit()
    if response is None:
        response = { 'body': "No student with sid={} found".format(sid) }
        return Response(json.dumps(response), status=500, content_type="application/json")
    response = { 'body': response }
    return Response(json.dumps(response), status=200, content_type="application/json")

def insert_one_student(sid, data):
    response = None
    sql = "INSERT INTO Students VALUES (%s, %s, %s, %s, %s, %s, %s);"
    first_name, last_name, email, phone, major, interests = None, None, None, None, None, None
    if "FirstName" in data.keys():
        first_name = data["FirstName"]
    if "LastName" in data.keys():
        last_name = data["LastName"]
    if "email" in data.keys():
        email = data["email"]
    if "phone" in data.keys():
        phone = data["phone"]
    if "major" in data.keys():
        major = data["major"]
    if "interests" in data.keys():
        interests = data["interests"]
    conn.ping()
    with conn.cursor() as cur:
        try:
            cur.execute(sql, (sid, first_name, last_name, email, phone, major, interests,))
            response = "{} row(s) inserted into Students table".format(cur.rowcount)
            print("SUCCESS: {} row(s) inserted into Students table".format(cur.rowcount))
        except Exception as e:
            response = {
                'message': "Cannot insert {} into Students table".format(sid),
                'error': str(e)
            }
            print("ERROR: Cannot insert {} into Students table".format(sid))
            return Response(json.dumps(response), status=500, content_type="application/json")
    conn.commit()
    response = { 'body': response }
    return Response(json.dumps(response), status=200, content_type="application/json")

def delete_one_student(sid):
    sql1 = "DELETE FROM SelectProject WHERE studentID = %s;"
    sql2 = "DELETE FROM EnrollCourse WHERE studentID = %s;"
    sql3 = "DELETE FROM Students WHERE studentID = %s;"
    conn.ping()
    with conn.cursor() as cur:
        try:
            cur.execute(sql1, (sid,))
            print("SUCCESS: {} row(s) deleted from SelectProject table".format(cur.rowcount))
            cur.execute(sql2, (sid,))
            print("SUCCESS: {} row(s) deleted from EnrollCourse table".format(cur.rowcount))
            cur.execute(sql3, (sid,))
            print("SUCCESS: {} row(s) deleted from EnrollCourse table".format(cur.rowcount))
            response = "{} deleted from Students table".format(sid)
        except Exception as e:
            print("ERROR: Cannot delete {} from Students table".format(sid))
            response = {
                'message': "Cannot delete {} from Students table".format(sid),
                'error': str(e)
            }
            return Response(json.dumps(response), status=500, content_type="application/json")
    conn.commit()
    response = { 'body': response }
    return Response(json.dumps(response), status=200, content_type="application/json")


@app.route("/students/<sid>/courses", methods=["GET", "POST", "DELETE"])
def courses(sid):
    crn = None
    if "crn" in request.values.keys():
        crn = request.values["crn"]

    if request.method == "GET":
        return get_courses(sid)
    elif request.method == "POST" and crn is not None:
        return insert_one_course(sid, crn)
    elif request.method == "DELETE":
        return delete_courses(sid, crn)
    else:
        response = { 'body': "Request method {} not allowed".format(request.method) }
        return Response(json.dumps(response), status=500, content_type="application/json")

def get_courses(sid):
    sql = "SELECT CRN from EnrollCourse WHERE studentID = %s;"
    response = []
    conn.ping()
    with conn.cursor() as cur:
        cur.execute(sql, (sid,))
        for row in cur:
            response.append(row)
    conn.commit()
    print("SUCCESS: {} item(s) retrieved from DB".format(len(response)))
    response = {
        'body': list( map(str, response) )
    }
    return Response(json.dumps(response), status=200, content_type="application/json")

def insert_one_course(sid, crn):
    sql = "INSERT INTO EnrollCourse VALUES (%s, %s);"
    response = None
    conn.ping()
    with conn.cursor() as cur:
        try:
            cur.execute(sql, (sid, crn,))
            print("SUCCESS: {} row(s) inerted into EnrollCourse table".format(cur.rowcount))
            response = "({}, {}) inserted into EnrollCourse table".format(sid, crn)
        except Exception as e:
            print("ERROR: Cannot insert ({}, {}) into EnrollCourse table".format(sid, crn))
            response = {
                'message': "Cannot insert ({}, {}) into EnrollCourse table".format(sid, crn),
                'error': str(e)
            }
            return Response(json.dumps(response), status=500, content_type="application/json")
    conn.commit()
    response = { 'body': response }
    return Response(json.dumps(response), status=200, content_type="application/json")

def delete_courses(sid, crn=None):
    if crn is None:
        sql = "DELETE FROM EnrollCourse WHERE studentID = %s;"
    else:
        sql = "DELETE FROM EnrollCourse WHERE studentID = %s and CRN = %s;"
    response = None

    response = delete_projects(sid, crn)
    if response.status == '500 INTERNAL SERVER ERROR':
        return response

    conn.ping()
    with conn.cursor() as cur:
        try:
            if crn is None:
                cur.execute(sql, (sid,))
            else:
                cur.execute(sql, (sid, crn,))
            print("SUCCESS: {} row(s) deleted from EnrollCourse table".format(cur.rowcount))
            response = "{} deleted from EnrollCourse table".format(sid)
        except Exception as e:
            print("ERROR: Cannot delete {} from EnrollCourse table".format(sid))
            response = {
                'message': "Cannot delete {} from EnrollCourse table".format(sid),
                'error': str(e)
            }
            return Response(json.dumps(response), status=500, content_type="application/json")
    conn.commit()
    response = { 'body': response }
    return Response(json.dumps(response), status=200, content_type="application/json")


@app.route("/students/<sid>/projects", methods=["GET", "POST", "DELETE"])
def projects(sid):
    crn, pid = None, None
    if "crn" in request.args.keys():
        crn = request.args["crn"]
    elif "crn" in request.form.keys():
        crn = request.form["crn"]
    if "pid" in request.args.keys():
        pid = request.args["pid"]
    elif "pid" in request.form.keys():
        pid = request.form["pid"]

    if request.method == "GET":
        return get_projects(sid, crn)
    elif request.method == "POST" and crn is not None and pid is not None:
        return insert_one_project(sid, crn, pid)
    elif request.method == "DELETE":
        return delete_projects(sid, crn, pid)
    else:
        response = { 'body': "Request method {} not allowed".format(request.method) }
        return Response(json.dumps(response), status=500, content_type="application/json")

def get_projects(sid, crn=None):
    if crn is None:
        sql = "SELECT projectID from SelectProject WHERE studentID = %s;"
    else:
        sql = "SELECT projectID from SelectProject WHERE studentID = %s and CRN = %s;"
    response = []
    conn.ping()
    with conn.cursor() as cur:
        if crn is None:
            cur.execute(sql, (sid,))
        else:
            cur.execute(sql, (sid, crn,))
        for row in cur:
            response.append(row)
    conn.commit()
    print("SUCCESS: {} item(s) retrieved from DB".format(len(response)))
    response = {
        'body': list( map(str, response) )
    }
    return Response(json.dumps(response), status=200, content_type="application/json")

def insert_one_project(sid, crn, pid):
    sql = "INSERT INTO SelectProject VALUES (%s, %s, %s);"
    response = None
    conn.ping()
    with conn.cursor() as cur:
        try:
            cur.execute(sql, (sid, crn, pid,))
            print("SUCCESS: {} row(s) inerted into SelectProject table".format(cur.rowcount))
            response = "({}, {}, {}) inserted into SelectProject table".format(sid, crn, pid)
        except Exception as e:
            print("ERROR: Cannot insert ({}, {}, {}) into SelectProject table".format(sid, crn, pid))
            response = {
                'message': "Cannot insert ({}, {}, {}) into SelectProject table".format(sid, crn, pid),
                'error': str(e)
            }
            return Response(json.dumps(response), status=500, content_type="application/json")
    conn.commit()
    response = { 'body': response }
    return Response(json.dumps(response), status=200, content_type="application/json")

def delete_projects(sid, crn=None, pid=None):
    response = None
    conn.ping()
    with conn.cursor() as cur:
        try:
            if crn is None and pid is None:
                cur.execute("DELETE FROM SelectProject WHERE studentID = %s;", (sid,))
            elif pid is None:
                cur.execute("DELETE FROM SelectProject WHERE studentID = %s and CRN = %s;", (sid, crn,))
            elif crn is None:
                cur.execute("DELETE FROM SelectProject WHERE studentID = %s and projectID = %s;", (sid, pid,))
            else:
                cur.execute("DELETE FROM SelectProject WHERE studentID = %s and CRN = %s and projectID = %s;", (sid, crn, pid,))
            print("SUCCESS: {} row(s) deleted from EnrollCourse table".format(cur.rowcount))
            response = "{} deleted from EnrollCourse table".format(sid)
        except Exception as e:
            print("ERROR: Cannot delete {} from EnrollCourse table".format(sid))
            response = {
                'message': "Cannot delete {} from EnrollCourse table".format(sid),
                'error': str(e)
            }
            return Response(json.dumps(response), status=500, content_type="application/json")
    conn.commit()
    response = { 'body': response }
    return Response(json.dumps(response), status=200, content_type="application/json")


# Start flask server
if __name__ == "__main__":
    try:
        port = os.environ['port']
    except:
        port = 5000
    app.run(port=port)
