# budgets.py
from flask import Blueprint, render_template
from flask_login import login_required

budgets = Blueprint('budgets', __name__)

@budgets.route('/')
@login_required
def index():
    return render_template('budgets/index.html')