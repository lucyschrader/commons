import requests, time, os
import flickr_api
from bs4 import BeautifulSoup

flickr_api_key = os.environ['FLICKR_API_KEY']
flickr_secret = os.environ['FLICKR_SECRET']

dnz_api_key = os.environ['DNZ_API_KEY']

# Commons keys
flickr_api.set_keys(api_key = flickr_api_key, api_secret = flickr_secret)

# TODO Write a preparation script to help create/source the necessary files
# Get DNZ and IE numbers from source lists
# Anything that will help get the tiffs, correctly named

def authenticate():
    a = flickr_api.auth.AuthHandler()
    perms = 'write'
    url = a.get_authorization_url(perms)
    print url
    verification_code = raw_input("Enter verification code: ")
    a.set_verifier(verification_code)
    flickr_api.set_auth_handler(a)
    a.save('auth_file')
    print "Authenticated!"
    return True

def get_auth():
    flickr_api.set_auth_handler('auth_file')
    return True

def check_auth():
    try:
        get_auth()
        print "Authenticated!"
    except:
        authenticate()

# A function to test authentication
def get_photo_numbers(username):
    user = flickr_api.Person.findByUserName(username)
    photos = user.getPhotos()
    print user
    print photos.info.total

def upload(dnz_id, IE_number):
    try:
        photo_path = ('files/%s.jpg' % IE_number)
#        photo_path = ('files/%s.tiff' % IE_number)
        metadata = get_metadata(dnz_id)
        title = metadata['title']
        description = add_citation(metadata['description'], dnz_id)
        flickr_api.upload(photo_file = photo_path, title = title, description = description)
        print '%s uploaded!' % title
        status = open('files/%s.status' % IE_number, 'a')
        status.close
        return True
    except:
        print "Unexpected error!", sys.exc_info()[0]
        raise
        failure = open('files/%s.failure' % IE_number, 'a')
        failure.close

def get_IE_number(dnz_id):
    api_url = 'http://api.digitalnz.org.nz/v3/records/%s.json?api_key=%s&fields=dc_identifier' % (str(dnz_id), dnz_api_key)
    response = requests.get(api_url).json()
#    print response['record']['dc_identifier']
    for i in response['record']['dc_identifier']:
        if 'ndha' in i:
            id_string = i
#            print id_string
            IE_number = id_string[7:]
            print "IE number for %s is %s" % (str(dnz_id), IE_number)
            return IE_number
        else:
            return None

def get_metadata(dnz_id):
    parameters = ['title','description']
    api_url = 'http://api.digitalnz.org/v3/records/%s.json?api_key=%s' % (str(dnz_id), dnz_api_key)
    response = requests.get(api_url).json()
    title = response['record']['title']
    description = response['record']['description']
    return {'title': title, 'description': description}

def add_citation(description, dnz_id):
    natlib_url = 'http://natlib.govt.nz/records/%s' % str(dnz_id)
    natlib_page = requests.get(natlib_url)
    natlib_html = natlib_page.text
    soup = BeautifulSoup(natlib_html)
    citation = soup.find("div", {"class": "usage"})
    citation = citation.span.text
    description = '%s \n\n %s' % (description, citation)
    return description

def main():
    no_of_uploads = introduction()
    check_auth()
    list_of_files = os.listdir('files')
    i = 0
    with open('data/commonsnumbers.txt') as f:
        for dnz_id in f:
            IE_number = get_IE_number(dnz_id)
            if '%s.status' % IE_number in list_of_files:
                print '%s.tiff already uploaded!' % IE_number
            else:
                if i == no_of_uploads:
                    break
                else:
                    if '%s.jpg' % IE_number in list_of_files:
#                    if '%s.tiff' % IE_number in list_of_files
                        if upload(dnz_id, IE_number) == True:
                            i += 1
                            if '%s.failure' % IE_number in list_of_files:
                                os.remove('files/%s.failure' % IE_number)

def introduction():
    print """
Welcome to the NATIONAL LIBRARY UPLOADING THINGS TO FLICKR interface.
Before we get started, make sure all the tiffs you're uploading are
sitting in the 'files' folder, and are named with their IE number and
the 'tiff' extension, like so: 209763.tiff

Make sure you've also got a file called 'dnz_numbers.txt', with the
DigitalNZ identifier of each image you want to upload on a new line.

All good to go? Enter the number of images you want to upload, or leave
it blank to top out at 50.
    """
    no_of_uploads = raw_input("> ")
    if no_of_uploads == None:
        no_of_uploads = 50
    else:
        no_of_uploads = int(no_of_uploads)
    return no_of_uploads

#login = authenticate()
#if login == True:
#get_auth()
#get_photo_numbers('National Library NZ on The Commons')

#check_auth()
#upload(22308338)

main()