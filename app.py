import datetime
from flask import Flask, render_template, request, render_template_string
from flask import jsonify
import json
from dateutil.relativedelta import relativedelta
import requests

app = Flask(__name__)


def analysis_file(filename):
    data = {}
    with open(filename) as f:
        for idx, line in enumerate(f):
            json_data = json.loads(line)
            temp = {}
            temp.update({'source_ip': json_data['source_ip']})
            date = datetime.datetime.strptime(json_data['timestamp']['$date'], "%Y-%m-%dT%H:%M:%S.%f%z").replace(
                tzinfo=None)
            temp.update({'date': date})
            dat = {idx: temp}
            data.update(dat)
    return data


def dict_to_set(dic):
    data = set()
    for v, k in dic.items():
        data.add(k['source_ip'])
    return data


def intersection_of_set(a, b):
    return list(a.intersection(b))


@app.route('/')
def hello_world():
    items1 = analysis_file('session_gokhan.json')
    # items2 = analysis_file('session2.json')

    # api request
    r = requests.get(
        'http://172.104.239.150/api/session/?api_key=576a6e2d696f4b2c9bf1101811287292&limit=1000')
    items3 = json.loads(r.text)
    items_api = {}
    for idx, data in enumerate(items3['data']):
        temp = {}
        temp.update({'source_ip': data['source_ip']})
        date = datetime.datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=None)
        temp.update({'date': date})
        dat = {idx: temp}
        items_api.update(dat)
    index1 = []
    a = dict_to_set(items1)
    b = dict_to_set(items_api)
    intersections = intersection_of_set(a, b)
    intersections_dict = {}

    for i in intersections:
        for value, key in items1.items():
            if i == key['source_ip']:
                index1.append(value)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        data = dict()
        for idx, i in enumerate(index1):
            date1 = items1[i]['date']
            date2 = items_api[idx]['date']
            temp = {}
            temp.update({'source_ip': items1[i]['source_ip']})
            temp.update({'date1': date1})
            difference = abs(relativedelta(date1, date2))
            temp.update({'date2': date2})
            temp.update({'difference': difference})
            dat = {idx: temp}
            intersections_dict.update(dat)
            template = """
                {% for key,value in intersections %}
                    <tr class="">
                        <td>{{ loop.index }}</td>
                        <td>{{ value['source_ip'] }}</td>
                        <td>{{ value['date1'] }}</td>
                        <td>{{ value['date2'] }}</td>
                        <td>{{ value['difference'] }} ago</td>
                    </tr>
                {% endfor %}
                """
            data['html_intersections'] = render_template_string(template,
                                                                intersections=intersections_dict.items())
        return jsonify(data)
    return render_template('index.html', items1=items1.items(), items2=items_api.items())


if __name__ == '__main__':
    app.run()
