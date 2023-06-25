# import functions_framework
from gmail_client import GmailClient


# @functions_framework.http
def handler(request):
    # request_json = request.get_json(silent=True)
    # request_args = request.args

    # if request_json and 'name' in request_json:
    #     name = request_json['name']
    # elif request_args and 'name' in request_args:
    #     name = request_args['name']
    # else:
    #     name = 'World'
    GmailClient().process_emails()
    return "done"


if __name__ == "__main__":
    handler({})
