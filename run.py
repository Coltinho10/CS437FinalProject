from app import create_app
from app.extensions import login_manager, bp

# Initialize the app
app, celery = create_app(login_manager=login_manager, bp=bp)
app.app_context().push()

if __name__ == "__main__":
    app.run(debug=True)