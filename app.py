from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key'
jwt = JWTManager(app)

# Dummy user data (replace with a proper user database)
users = {
    'user1': 'password1',
    'user2': 'password2',
}

# Dummy throttle implementation
throttle_counter = 0
throttle_limit = 5

# JWT authentication
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username in users and users[username] == password:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# Throttle middleware
@app.before_request
def limit_request():
    global throttle_counter
    if throttle_counter >= throttle_limit:
        return jsonify({"message": "API rate limit exceeded"}), 429
    throttle_counter += 1

# File upload and result page
@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template('result.html', filename=filename)

# Zoom functionality page
@app.route('/zoom/<filename>')
def zoom_image(filename):
    return render_template('view.html', filename=filename)

if __name__ == '__main__':
    app.run(debug=True)
