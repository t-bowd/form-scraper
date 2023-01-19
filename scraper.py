from bs4 import BeautifulSoup
from requests_html import HTMLSession
from urllib.parse import urlparse
import sys
import requests
import time

session = HTMLSession()

def get_all_forms(url):
    r = session.get(url)
    r.html.render()
    soup = BeautifulSoup(r.html.html, "html.parser")
    return soup.find_all("form")

def get_form_details(form):
    details = {}
    action = form.attrs.get("action")
    method = form.attrs.get("method", "get")
    inputs = []
    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        input_value = input_tag.attrs.get("value", "")
        inputs.append({"type": input_type, "name": input_name, "value": input_value})
    for select in form.find_all("option"):
        select_name = select.attrs.get("name")
        select_type = "select"
        select_options = []
        select_default_value = ""
        for select_option in select.find_all("option"):
            option_value = select_option.attrs.get("value")
            if option_value:
                select_options.append(option_value)
                if select_options.attrs.get("selected"):
                    select_default_value = option_value
        if not select_default_value and select_options:
            select_default_value = select_options[0]
        inputs.append({"type": select_type, "name": select_name, "values": select_options, "value": select_default_value})
    for textarea in form.find_all("textarea"):
        textarea_name = textarea.attrs.get("name")
        textarea_type = "textarea"
        textarea_value = textarea.attrs.get("value", "")
        inputs.append({"type": textarea_type, "name": textarea_name, "value": textarea_value})    
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details

def send_request(url, data):
    try:
        r = requests.post(url, data)
        #print(f"Payload sent: {data}")
    except requests.exceptions.Timeout:
        print("Timeout: Going to sleep for 60s")
        time.sleep(60)
        send_request(url, data)
    except requests.exceptions.RequestException as e:
        print("Catastrophic error: exiting")
        raise SystemExit(e)
    except requests.exceptions.TooManyRedirects:
        print("Bad URL, try again")
        sys.exit()
    else:
        print("="*100)
        print("="*100)
        print(r.content)
        return True 
           




if __name__ == "__main__":
    url = sys.argv[1]
    forms = get_all_forms(url)
    for i, form in enumerate(forms, start=1):
        form_details = get_form_details(form)
        print("="*50, f"form #{i}", "="*50)
        print(form_details)

    choice = int(input("Select your form: "))
    form_details = get_form_details(forms[choice-1])
    data = {}
    for input_tag in form_details["inputs"]:
        if input_tag["type"] == "hidden":
            data[input_tag["name"]] = input_tag["value"]
        elif input_tag["type"] == "select":
            for i, option in enumerate(input_tag["values"], start=1):
                if option == input_tag["value"]:
                    print(f"{i} # {option} (default)")
                else: 
                    print(f"{i} # {option}")
            choice = input(f"Enter the option for the field '{input_tag['name']}' (1-{i}): ")
            try:
                choice = int(choice)
            except:
                value = input_tag["value"]
            else:
                value  = input_tag["values"][choice-1]
            data[input_tag["name"]] = value
        elif input_tag["type"] != "submit":
            value = input(f"Enter the value for the field '{input_tag['name']}' (type: {input_tag['type']}): ")
            data[input_tag["name"]] = value       
    if form_details["action"]:
        request_url = form_details["action"]
    else:
        data["action"] = "elementor_pro_forms_send_form"
        data["referrer"] = "http://" + urlparse(url).netloc
        request_url = "http://" + urlparse(url).netloc + "/wp-admin/admin-ajax.php"
    send_request(request_url, data)                                                    