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


def dictionary_to_set(dic):
    data = set()
    for v, k in dic.items():
        data.add(k['source_ip'])
    return data


def intersection_of_set(a, b):
    return list(a.intersection(b))


@app.route('/')
def analysis_attacker_informations():
    attacker_informations_dictionary_gokhan = analysis_file('session_gokhan.json')
    # items2 = analysis_file('session2.json')
    api_key_file = open("api_key.txt", "r")
    api_key = api_key_file.read()
    # api request
    r = requests.get(api_key)
    attacker_informations_dictionary_gokhan_in_json = json.loads(r.text)
    attacker_informations_dictionary_omer = {}
    for idx, data in enumerate(attacker_informations_dictionary_gokhan_in_json['data']):
        temp = {}
        temp.update({'source_ip': data['source_ip']})
        date = datetime.datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=None)
        temp.update({'date': date})
        dat = {idx: temp}
        attacker_informations_dictionary_omer.update(dat)
    attacker_informations_list_gokhan = []
    a = dictionary_to_set(attacker_informations_dictionary_gokhan)
    b = dictionary_to_set(attacker_informations_dictionary_omer)
    intersections = intersection_of_set(a, b)
    intersections_dict = {}

    for i in intersections:
        for value, key in attacker_informations_dictionary_gokhan.items():
            if i == key['source_ip']:
                attacker_informations_list_gokhan.append(value)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        data = dict()
        for idx, i in enumerate(attacker_informations_list_gokhan):
            date1 = attacker_informations_dictionary_gokhan[i]['date']
            date2 = attacker_informations_dictionary_omer[idx]['date']
            temp = {}
            temp.update({'source_ip': attacker_informations_dictionary_gokhan[i]['source_ip']})
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
    return render_template('index.html', items1=attacker_informations_dictionary_gokhan.items(), items2=attacker_informations_dictionary_omer.items())


if __name__ == '__main__':
    app.run()
