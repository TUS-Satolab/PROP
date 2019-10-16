# project/server/__init__.py


import os

from flask import Flask


def create_app(script_info=None):

    # instantiate the app
    app = Flask(
        __name__,
        template_folder='../client/templates'
    )

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)


    return app