import os
from flask import Flask, request, jsonify, send_file
from script.apps_data_se import get_apps_data
app = Flask(__name__)


@app.route('/get-apps-data', methods = ['POST'])
def get_data():
    data = request.get_json()
    category = data.get('category')
    country_code = data.get('country_code')

    if not category or not country_code:
        return jsonify({"error": "Both 'category' and 'country_code' are required."}), 400
    
    file_path = get_apps_data(category, country_code)
    
    if not os.path.exists(file_path):
        return jsonify({"error": f"File not found: {file_path}"}), 404
    
    return send_file(
        file_path,
        mimetype='text/csv',
        as_attachment=True,
        download_name=os.path.basename(file_path)
    )

if __name__ == '__main__':
    app.run(debug=True)