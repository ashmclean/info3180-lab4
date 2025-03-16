import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile
from app.forms import LoginForm, UploadForm
from werkzeug.security import check_password_hash

app.config['UPLOAD_FOLDER'] = 'uploads' 
###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    form = UploadForm()

    if form.validate_on_submit():
        # Handle the file upload logic here
        file = form.file.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        flash("File uploaded successfully!", "success")
        return redirect(url_for("home"))  # Redirect to a relevant page after upload

    return render_template("upload.html", form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    # change this to actually validate the entire form submission
    # and not just one field
    if form.validate_on_submit():  # ✅ Proper form validation
        username = form.username.data
        password = form.password.data
    
        user = UserProfile.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)  # ✅ Log in user
            flash("Login successful! Welcome back.", "success")  # ✅ Success message
            return redirect(url_for("upload"))  # ✅ Redirect to upload page

        flash("Invalid username or password. Please try again.", "danger") 

        # Remember to flash a message to the user
        return redirect(url_for("home"))  # The user should be redirected to the upload form instead
    return render_template("login.html", form=form)

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


def get_uploaded_images():
    # Get the absolute path to the uploads folder
    upload_dir = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])
    # Get a list of files in the directory (only images)
    return [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]

@app.route('/uploads/<filename>')
def get_image(filename):
    # Send the image file from the uploads folder
    return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)

# Route to list all uploaded images in the uploads folder
@app.route('/files')
@login_required
def files():
    # Get the list of uploaded images
    images = get_uploaded_images()
    # Render a template with the list of images
    return render_template('files.html', images=images)