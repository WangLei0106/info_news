from flask import Blueprint


index_blu = Blueprint('index', __name__)

from info.modules.index import views