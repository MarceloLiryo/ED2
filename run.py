from flask import Flask
from app.routes.home import home_bp
from app.routes.admin import admin_bp


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="app/templates",
        static_folder="app/static",
    )
    app.secret_key = "globalsim-ed2-uneb-secret-key"

    app.register_blueprint(home_bp)
    app.register_blueprint(admin_bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
