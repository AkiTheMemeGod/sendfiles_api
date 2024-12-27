from flask import Flask, request, render_template, send_file, flash, redirect, jsonify
import secrets
from assets import Database
import io
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

db = Database()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/send', methods=['GET', 'POST'])
def send_files():
    if request.method == 'POST':
        # Generate a 6-digit key
        share_key = secrets.randbelow(10**6)
        share_key = str(share_key).zfill(6)

        uploaded_files = request.files.getlist('files')
        if uploaded_files:
            for file in uploaded_files:
                file_data = file.read()
                db.send_files(share_key, file.filename, file_data)

            flash(f"Files successfully uploaded! Share key: {share_key}", "success")
        else:
            flash("No files uploaded.", "danger")

        return redirect('/send')

    return render_template('send.html')


@app.route('/api/send', methods=['POST'])
def api_send_files():
    if request.method == 'POST':
        # Generate a 6-digit key
        share_key = secrets.randbelow(10**6)
        share_key = str(share_key).zfill(6)

        # Get the uploaded files
        uploaded_files = request.files.getlist('files')
        if uploaded_files:
            for file in uploaded_files:
                file_data = file.read()
                db.send_files(share_key, file.filename, file_data)

            # Return success response with share key
            return {
                "message": "Files successfully uploaded!",
                "share_key": share_key
            }, 200  # HTTP Status Code 200 means OK
        else:
            # Return error if no files are uploaded
            return {
                "message": "No files uploaded.",
            }, 400  # HTTP Status Code 400 means Bad Request



@app.route('/receive', methods=['GET', 'POST'])
def receive_files():
    files = None
    if request.method == 'POST':
        share_key = request.form.get('code', '').zfill(6)
        files = db.get_files(share_key)

        if not files:
            flash("Key not found. Please check the key and try again.", "danger")

    return render_template('receive.html', files=files)


@app.route('/api/receive', methods=['POST'])
def api_receive_files():
    files = None
    if request.method == 'POST':
        share_key = request.form.get('code', '').zfill(6)

        files = db.get_files(share_key)

        if not files:
            return {
                "message": "Key not found. Please check the key and try again.",
            }, 404

        return {
            "message": "Files found.",
            "files": [{"id": file[0], "filename": file[1], "preview": file[2]} for file in files]
        }, 200


@app.route('/download/<int:file_id>')
def download_file(file_id):
    result = db.get_file_data(file_id)
    if result:
        filename, filedata = result
        db.delete_file(file_id)
        return send_file(
            io.BytesIO(filedata),
            download_name=filename,
            as_attachment=True
        )
    else:
        flash("File not found.", "danger")
        return redirect('/receive')


if __name__ == '__main__':
    app.run(debug=True)
