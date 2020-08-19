"""app/run.py
"""
import os

from flask import Flask

from common.utility import err_response
from config import config
from apis.views.handler import apis

app = Flask(__name__,
            static_folder='apis/static',
            template_folder='apis/templates')
app.config.from_object(config)

app.register_blueprint(apis)


@app.errorhandler(404)
@app.errorhandler(500)
def errorhandler(error):
    """errorhandler
    """
    return err_response(error=error), error.code


def main():
    """main
    """
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    app.run(host=host, port=port)


if __name__ == '__main__':
    main()
