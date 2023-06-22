import functions_framework
import imaplib
import logging
import os

user = os.environ.get('WATCH_EMAIL', 'contact.fuzzylabs@gmail.com')
password = os.environ.get('WATCH_PASSWORD', 'xjvqkodofonrhzxe')
imap_url = 'imap.gmail.com'

@functions_framework.http
def handler(request):
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'name' in request_json:
        name = request_json['name']
    elif request_args and 'name' in request_args:
        name = request_args['name']
    else:
        name = 'World'

    # this is done to make SSL connection with GMAIL
    con = imaplib.IMAP4_SSL(imap_url)

    # logging the user in
    con.login(user, password)

    # calling function to check for email under this label
    con.select('Inbox')

    result_bytes = search('FROM', 'no-reply@accounts.google.com', con)

    # fetching emails from this user "tu**h*****1@gmail.com"
    msgs = get_emails(result_bytes, con)

    # Uncomment this to see what actually comes as data
    # print(msgs)


    # Finding the required content from our msgs
    # User can make custom changes in this part to
    # fetch the required content he / she needs

    # printing them by the order they are displayed in your gmail
    for msg in msgs[::-1]:
        for sent in msg:
            if type(sent) is tuple:

                # encoding set as utf-8
                content = str(sent[1], 'utf-8')
                data = str(content)

                # Handling errors related to unicodenecode
                try:
                    indexstart = data.find("ltr")
                    data2 = data[indexstart + 5: len(data)]
                    indexend = data2.find("</div>")

                    # printing the required content which we need
                    # to extract from our email i.e our body
                    logging.info(data2[0: indexend])

                except UnicodeEncodeError as e:
                    pass

    return f"There where {len(msgs)} messages. Can you believe!"

# Function to get email content part i.e its body part
def get_body(msg):
	if msg.is_multipart():
		return get_body(msg.get_payload(0))
	else:
		return msg.get_payload(None, True)

# Function to search for a key value pair
def search(key, value, con):
	result, data = con.search(None, key, '"{}"'.format(value))
	return data

# Function to get the list of emails under this label
def get_emails(result_bytes, con):
	msgs = [] # all the email data are pushed inside an array
	for num in result_bytes[0].split():
		typ, data = con.fetch(num, '(RFC822)')
		msgs.append(data)

	return msgs