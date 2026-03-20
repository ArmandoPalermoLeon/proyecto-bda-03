import os 
from flask import Flask, render_template, request, redirect, url_for, flash
import db

app=Flask(__name__)
app.secret_key="clave"
@app.route("/")
def index():
    pass

if __name__=="__main__":
    app.run(debug=True)

