import requests
import sys
import time

first_name = "gary"
last_name = "gary"
email = "gary@gary.c"
url = "https://www.calibeach.com.au/wp-admin/admin-ajax.php"

data = {
     "post_id" : "447",
     "form_id" : "5c695271",
     "referer_title" : "Cali Beach - Gold Coast - Australia",
     "queried_id" : "411",
     "form_fields[field_e9687e4]" : first_name,
     "form_fields[field_6b39102]" : last_name, 
     "form_fields[email]" : email, 
    "action" : "elementor_pro_forms_send_form",
    "referrer" : "https://www.calibeach.com.au/"
}

def send_request():
    try:
        r = requests.post(url, data)
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
        print(r.content)
        return True



if __name__ == "__main__":
    send_request()