import requests
import json

from django.conf import settings


def create_pad(pad_id):
    """
    Creates a new etherpad with the given id and initial text
    """
    params = {
        'apikey': settings.ETHERPAD_API_KEY,
        'padID': pad_id,
        'text': ''
    }
    return make_request('createPad', params)
    
def delete_pad(pad_id):
    """
    Deletes a etherpad with the given id
    """
    params = {
        'apikey': settings.ETHERPAD_API_KEY,
        'padID': pad_id
    }
    return make_request('deletePad', params)
    
def list_pads():
    """
    Lists all created pads
    """
    params = {
        'apikey': settings.ETHERPAD_API_KEY
    }
    return make_request('listAllPads', params)
    
def get_text(pad_id):
    """
    Retrieves the text of the given pad
    """
    params = {
        'apikey': settings.ETHERPAD_API_KEY,
        'padID': pad_id,
    }
    return make_request('getText', params)

def append_text(pad_id, text):
    """
    Appends text to the given pad
    """
    params = {
        'apikey': settings.ETHERPAD_API_KEY,
        'padID': pad_id,
        'text': text
    }
    return make_request('appendText', params)

def get_html(pad_id):
    """
    Retrieves the html of the given pad
    """
    params = {
        'apikey': settings.ETHERPAD_API_KEY,
        'padID': pad_id,
    }
    return make_request('getHTML', params)
    
def set_html(pad_id, html):
    """
    Retrieves the html of the given pad
    """
    params = {
        'apikey': settings.ETHERPAD_API_KEY,
        'padID': pad_id,
        'html': html
    }
    return make_request('setHTML', params)
    
#--- Utility ---#
def print_pretty_json(json_data):
    """
    Pretty prints a json object to the console
    """
    json_obj = json.loads(json_data)
    json_pretty = json.dumps(json_obj, indent=4, sort_keys=True)
    print(json_pretty)


#--- Request ---#
def make_request(command, params):
    """
    Makes a request to the etherpad-lite API
    """
    try:
        response = requests.post(settings.ETHERPAD_API_ENDPOINT + str(command), data=params)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Something went wrong: {err}")
    else:
        if response.status_code == 200:
            #print_pretty_json(response.content)
            return json.loads(response.content)
        else:
            try:
                error_message = response.json()['message']
            except (KeyError, ValueError):
                error_message = response.content.decode('utf-8')
            if error_message:
                raise requests.exceptions.RequestException(f'Error creating new pad: {error_message}')
            else:
                raise requests.exceptions.RequestException('Error creating new pad')
