import pandas
from flask import Flask, render_template, flash, request, redirect
from geopy.geocoders import ArcGIS

import requests
from bs4 import BeautifulSoup

nom = ArcGIS()
app = Flask(__name__)
UPLOAD_FOLDER = '/media/aniket/D/GeoCoderApp/files/'
ALLOWED_EXTENSIONS = {'csv'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def home_page():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # df = pandas.read_csv('/media/aniket/D/GeoCoderApp/files/' + filename)
            df = pandas.read_csv(file)

            # if 'Address' not in df.columns.values.tolist():
            #     return render_template('home.html', error=error)
            col_list = []
            for col in df.columns.values.tolist():
                col_list.append(col.lower())

            if 'address' not in col_list:
                msg = 'CSV file should have one column named Address or address'
                return render_template('home.html', msg=msg)
            else:
                df["address"] = df["address"] + "," + df["City"] + "," + df["State"] + "," + df["Country"]
                df['Latitude'] = df["address"].apply(nom.geocode).apply(lambda x: x.latitude if x != None else None)
                df['Longitude'] = df["address"].apply(nom.geocode).apply(
                    lambda y: y.longitude if y != None else None)
                df.to_csv(UPLOAD_FOLDER.__add__(file.filename))
                msg = "File uploaded successfully!"
                global table
                table = df.to_html()

                return render_template('home.html', msg=msg, table=table)
        else:
            msg = 'Please upload csv file.'
            return render_template('home.html', msg=msg)

    else:
        return render_template('home.html')


@app.route('/download', methods=['GET', 'POST'])
def download_csv():
    if request.method == 'POST':
        r = requests.get('http://localhost:5000/download')
        s = BeautifulSoup(r.content, 'html.parser')

        # empty list
        data = []

        # for getting the header from
        # the HTML file
        list_header = []
        header = s.find_all("table")[0].find("tr")

        for items in header:
            try:
                list_header.append(items.get_text())
            except:
                continue

        # for getting the data
        html_data = s.find_all("table")[0].find_all("tr")[1:]

        for element in html_data:
            sub_data = []
            for sub_element in element:
                try:
                    sub_data.append(sub_element.get_text())
                except:
                    continue
            data.append(sub_data)

            # Storing the data into Pandas
        # DataFrame
        data_frame = pandas.DataFrame(data=data, columns=list_header)

        # Converting Pandas DataFrame
        # into CSV file
        data_frame.to_csv('output.csv')
        return render_template('home.html', table=table)

    else:
        return render_template('home.html', table=table)


if __name__ == '__main__':
    app.run(debug=True)
