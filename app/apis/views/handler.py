"""app/apis/views/handler.py
"""
from flask import Blueprint, jsonify, request

from common.utility import err_response
from apis.views.api import handler as api_handler
from apis.views.app import handler as app_handler

apis = Blueprint(name='rasp-iccar', import_name=__name__,
                 url_prefix='/rasp-iccar')


@apis.route('/healthcheck', methods=['GET'])
def healthcheck():
    """healthcheck
    """
    return jsonify({'status': 'healthy'}), 200


@apis.route('/api', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api():
    """api
    """
    if request.method == 'GET':
        process = request.args.get('process')
        req = {
            'param1': request.args.get('request'),
            'param2': request.args
        }

        if process == 'back_end':
            return api_handler(req=req)

        if process == 'front_end':
            return app_handler(req=req)

    if request.method == 'POST' or request.method == 'PUT' or request.method == 'DELETE':
        payload = request.json
        process = payload.get('process')
        req = payload.get('request')

        if process == 'back_end':
            return api_handler(req=req)

    return jsonify({'message': 'no route matched with those values'}), 200


@apis.errorhandler(404)
@apis.errorhandler(500)
def errorhandler(error):
    """errorhandler
    """
    return err_response(error=error), error.code
