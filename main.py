import json
import os
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import datetime
import requests
from datetime import timedelta, date
import time

PUBLIC_KEY = os.environ['DISCORD_PUBLIC_KEY']


def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])

        signature = event['headers']['x-signature-ed25519']
        timestamp = event['headers']['x-signature-timestamp']

        # validate the interaction

        verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))

        message = timestamp + json.dumps(body, separators=(',', ':'))

        try:
            verify_key.verify(message.encode(),
                              signature=bytes.fromhex(signature))
            print("Good key")
        except BadSignatureError:
            print("Bad Key")
            return {
                'statusCode': 401,
                'body': json.dumps('invalid request signature')
            }

        # handle the interaction

        type = body['type']

        if type == 1:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'type': 1
                })
            }

        elif type == 2:
            return command_handler(body)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps('unhandled request type')
            }
    except:
        raise


def command_handler(body):
    command = body['data']['name']

    if command == 'hello':
        return {
            'statusCode': 200,
            'body': json.dumps({
                'type': 4,
                'data': {
                    'content': 'Hello, World.',
                }
            })
        }
        
    elif command == "issflyover":
        N2YO_KEY = os.environ['N2YO_KEY']
        

        data = requests.get(f"https://api.n2yo.com/rest/v1/satellite/visualpasses/25544/{body['data']['options'][0]['value']}/{body['data']['options'][1]['value']}/0/10/10/&apiKey={N2YO_KEY}",
                            timeout=3
                            )
        visual = data.json()
        
        count = 0
        while count<len(visual['passes']):
            information = f"""
            Next ISS flyover schedule information for your area \n
                Time Visible {round(visual['passes'][count]['duration'] / 60, 2)} minutes \n
                Max visual magnitude: {visual['passes'][count]['mag']} \n
                Start Date & Time: {datetime.datetime.fromtimestamp(visual['passes'][count]['startUTC'])} EST
                Start Azmuth: {visual['passes'][count]['startAz']}, {visual['passes'][count]['startAzCompass']}
                Start Elevation: {str(visual['passes'][count]['startEl'])} \n
                Max Azmuth Start Date & Time: {datetime.datetime.fromtimestamp(visual['passes'][count]['maxUTC'])} EST
                Max Azmuth: {visual['passes'][count]['maxAz']}, {visual['passes'][count]['maxAzCompass']}
                Max Elevation: {str(visual['passes'][count]['maxEl'])} \n 
                End Date & Time: {datetime.datetime.fromtimestamp(visual['passes'][count]['endUTC'])} EST
                End Azmuth: {visual['passes'][count]['endAz']}, {visual['passes'][count]['endAzCompass']}
                End Elevation: {str(visual['passes'][count]['endEl'])} \n
            
        """
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'type': 4,
                    'data': {
                        'content': information,
                    }
                })
            }
            
    elif command == "nearearthobjects":
        key = os.environ['NASA_KEY']
        discord_key = os.environ['DISCORD_TOKEN']
        
        headers = {
            "Authorization": f"Bot {discord_key}",
            "Content-Type": "application/json"
            }
        
        interaction_url = f"https://discord.com/api/v10/interactions/{body['id']}/body['token']/callback"
        interaction_confirmation = {
            'statusCode': 200,
            'body': json.dumps({
                'type': 1
            })
        }
        
        interaction_response = requests.post(interaction_url, headers=headers, json=interaction_url)
        
        response = requests.get(
        f"https://api.nasa.gov/neo/rest/v1/feed?start_date={datetime.date.today()}&end_date={datetime.date.today() + timedelta(days=1)}&api_key={key}", 
        timeout=30
        )
        
        channel = body['channel']['id']
        response= response.json()
        
        
        
        if str(date.today()) not in response['near_earth_objects']:
            neo_data = f"No Objects Coming Near Earth In The Next 24 Hours. \n"
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'type': 4,
                    'data': {
                        'content': neo_data,
                    }
                })
            }
            
            
        elif str(date.today()) in response['near_earth_objects']:
                    
            listings = []
            neo_data = ""
            for neo in response['near_earth_objects'][str(date.today())]:
                next_neo = f"""\n
                    Name: {neo['name']},
                    NASA JPL Link: {neo['nasa_jpl_url']}
                    Estimated Minimum Diameter In Kilometers: {neo['estimated_diameter']['kilometers']['estimated_diameter_min']}
                    Estimated Maximum Diameter In Kilometers: {neo['estimated_diameter']['kilometers']['estimated_diameter_max']}
                    Close Approach Date: {neo['close_approach_data'][0]['close_approach_date_full']}
                    Velocity In Meters Per Second: {neo['close_approach_data'][0]['relative_velocity']['kilometers_per_second']}
                    Velocity In Meters Per Hour: {neo['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']}
                    Miss Distance In Kilometers: {neo['close_approach_data'][0]['miss_distance']['kilometers']}
                    Potentially Pazardous?: {neo['is_potentially_hazardous_asteroid']}
                    """
                if len(neo_data)+len(next_neo) < 2000:
                    neo_data += next_neo
                elif len(neo_data)+len(next_neo) > 2000:
                    listings.append(neo_data)
                    neo_data = ""
            
            neo_data = f"{len(response['near_earth_objects'][str(date.today())])} Objects Coming Near Earth In The Next 24 Hours. \n"
        
            data = {
                    "content": neo_data
                    }
                    
            channel_send = requests.post(f"https://discord.com/api/v10/channels/{channel}/messages", headers=headers, json=data)
            if channel_send.status_code != 200:
                print(f"Error sending message: {channel_send.text}")
            
            for listing in listings:    
                data = {
                    "content": listing
                    }
                channel_send = requests.post(f"https://discord.com/api/v10/channels/{channel}/messages", headers=headers, json=data)
                if channel_send.status_code != 200:
                    print(f"Error sending message: {channel_send.text}")
                    break
                time.sleep(0.1)
                
                
        
        
                
    elif command == "peopleinspace":
        discord_key = os.environ['DISCORD_TOKEN']
        
        interaction_url = f"https://discord.com/api/v10/interactions/{body['id']}/body['token']/callback"
        interaction_confirmation = {
                'statusCode': 200,
                'body': json.dumps({
                    'type': 1
                })
            }
        headers = {
            "Authorization": f"Bot {discord_key}",
            "Content-Type": "application/json"
            }
        interaction_response = requests.post(interaction_url, headers=headers, json=interaction_url)
        
        
        
        
        channel = body['channel']['id']
        space_get = requests.get('http://api.open-notify.org/astros.json',
                                timeout=3
                                )
    
        space_response = space_get.json()
        my_data = {}
        
        for item in space_response['people']:
            if not my_data.get(item['craft']):
                my_data[item['craft']] = [item['name']]
                continue
        
            my_data[item['craft']].append(item['name'])
        
        total_counter = 0
        
        stations, current = '', ''
        
        for station, names in my_data.items():
            total_counter += len(names)
            current = f"{len(names)} on board the {station}:\n"
        
            for name in names:
                current += f"- {name}\n"
        
            stations += f"{current}\n"
        
        total = f"There are currently {space_response['number']} people in space on board the following spacecrafts\n\n{stations}"
        
        
        
        
        
        data = {
                "content": total
                }
        headers = {
            "Authorization": f"Bot {discord_key}",
            "Content-Type": "application/json"
            }
        return {
            'statusCode': 200,
            'body': json.dumps({
                'type': 4,
                'data': {
                    'content': total,
                }
            })
        }
        
        
        
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('unhandled command')
        }
