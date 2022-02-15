import requests as rq
import time
import os
import json

from twilio.rest import Client
from datetime import datetime
import config_twilio as tw


def alert_to_admin():
    os.system(f'msg {tw.user_name} /server: {tw.user_name} my message')

    account_sid = tw.sid
    auth_token = tw.token
    client = Client(account_sid, auth_token)

    call = client.calls.create(
        twiml='<Response><Say>Alarm! Service is down!</Say></Response>',
        to=tw.to_number,
        from_=tw.from_number
    )
    print(call.sid)


def request(site_name, first=True):
    try:
        while True:
            response = rq.get(site_name)
            status_code = str(response.status_code)
            # status_code = '999'  # for error
            if status_code == '200':
                print(datetime.now().strftime("%d-%m-%Y %H:%M") + f' Site available: {site_name},'
                                                                  f' status code: {status_code}')
                time.sleep(60)
                continue
            else:
                print('WARNING!' + status_code)
                time.sleep(60)

                if first:
                    print('site unavailable' + status_code + '\nAlert to administration'
                                                             '\nApache will be restarting, after 5 minutes...')
                    alert_to_admin()
                    time.sleep(300)
                    request(site_name, False)
                else:
                    print('site unavailable' + status_code + '\nApache restarting...')
                    os.system('httpd -k restart')
                    time.sleep(300)
                    request(site_name)

    except rq.ConnectionError:
        print('Apache unavailable\nApache starting...')

        alert_to_admin()

        os.system('httpd -k start')
        time.sleep(60)
        request(site)


if __name__ == '__main__':

    with open('config_sites.json') as f:
        my_data = json.load(f)

    for key in my_data:
        print(f"Name: {key}; Site: {my_data[key]}")

    site = input(f'Enter site name for checking or new for add new entry:\n')

    if my_data.get(site) is None:
        print("Name dont find!")
        new_site = input("Enter new site name for add entry")
        new_address = input("Enter new address for site")

        my_data[new_site] = new_address
        new_my_data = json.dumps(my_data)

        with open('config_sites.json', 'w') as f:
            f.write(new_my_data)
        request(new_address)
    else:
        request(my_data.get(site))
