from flask import Flask, render_template, request, redirect, url_for, flash


app=Flask(__name__)
app.secret_key="clave"
@app.route("/", method=["POST"])
def index():
    return render_template('base.html')

if __name__=="__main__":
        app.run(debug=True)
