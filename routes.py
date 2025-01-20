from controllers.dogs_server import dogs_blueprint

def initial_routes(app):
    app.register_blueprint(dogs_blueprint)