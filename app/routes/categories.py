# categories.py
from flask import Blueprint, render_template
from flask_login import login_required

categories = Blueprint('categories', __name__)

@categories.route('/')
@login_required
def index():
    return render_template('categories/index.html')