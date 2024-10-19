# # test_twilio.py
# from twilio.rest import Client
# import os
# from dotenv import load_dotenv

# load_dotenv()

# account_sid = os.getenv('TWILIO_ACCOUNT_SID')
# auth_token = os.getenv('TWILIO_AUTH_TOKEN')

# client = Client(account_sid, auth_token)

# try:
#     client.api.accounts(account_sid).fetch()
#     print("Twilio credentials are valid.")
# except Exception as e:
#     print("Twilio credentials are invalid:", e)

