from flask import Flask, render_template, flash, request, Markup, \
    session, redirect, url_for, escape, Response, abort, send_file
from frML import app
from frML import convert
from werkzeug import secure_filename
import os

ALLOWED_EXTENSIONS = set(['xlsx', 'xls'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/convert/", methods=["POST", "GET"])
def converter():
    XMLfilename='fr-ML.xml'
    if (request.method=="POST"):
        xls_file = request.files['file']
        if ((xls_file) and allowed_file(xls_file.filename)):
            input_data = request.files['file'].stream.read()
            input_filename = None
            try:
                result = convert.convert(input_filename, 
                                         input_data, 
                                         "frML/static/data/"+XMLfilename)
                error = None
            except Exception, e:
                result = False
                # Can we pass nicer error messages to the user?
                error = "There was an unknown error. Please ensure your data \
                is correctly formatted according to a predefined template."
                error = e
                pass
        else:
            error = "That file extension is not permitted. Files must be of \
            the format: " + ", ".join(ALLOWED_EXTENSIONS)
            result = False
    else:
        erorr=""
        input_filename = "frML/source/projects.xlsx"
        input_data = open(input_filename).read()
        result = convert.convert(input_filename, 
                                 input_data, 
                                 "frML/static/data/"+XMLfilename)

    return render_template("convert.html", 
                           result=result,
                           XMLfilename=XMLfilename,
                           error=error)
