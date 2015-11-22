import requests, untangle, re, time, flickr_api, os
from flickr_api.api import flickr

flickr_api_key = os.environ['FLICKR_API_KEY']
flickr_secret = os.environ['FLICKR_SECRET']

flickr_api.set_keys(api_key = flickr_api_key, api_secret = flickr_secret)

flickr_base_url = 'https://api.flickr.com/services/rest/?method='
photo_list_method = 'flickr.people.getPhotos'
photo_method = 'flickr.photos.getInfo'

dnz_api_key = os.environ['DNZ_API_KEY']

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

def create_free_download_list():
    # DigitalNZ parameter identifying the pool
    facet = "and[atl_free_download]=True"
    
    # Search to check how many images there are, so I can call for the right number of pages of results
    result_count_url = "http://api.digitalnz.org/v3/records.json?api_key=%s&%s&per_page=0" % (dnz_api_key, facet)
    results_count_json = requests.get(result_count_url).json()
    count = results_count_json['search']['result_count']
    pages = count / 100 + 2

    # Create a new document to store the ID numbers
    with open('freedownloads.txt', 'w') as f:
        for page in range(1, pages):
            search_url = "http://api.digitalnz.org/v3/records.json?api_key=%s&%s&per_page=100&page=%d" % (dnz_api_key, facet, page)
            search_json = requests.get(search_url).json()
            for result in search_json['search']['results']:
                dnz_id = result['id']
                f.write('%s\n' % dnz_id)

def get_flickr_ids():
    username = "National Library NZ on The Commons"
    user = flickr_api.Person.findByUserName(username)
    photostream = user.getPublicPhotos
    w = flickr_api.Walker(photostream)
    flickr_ids = []
    for photo in w:
        if photo:
            flickr_ids.append(int(photo.id))
    return flickr_ids

def get_pool_ids():
    pool_ids = []
    with open('freedownloads.txt', 'r') as f:
        for line in f:
            number = int(line)
            pool_ids.append(number)
    return pool_ids

def get_photo_info():
    n = 1
    flickr_ids = get_flickr_ids()
    print 'Flickr IDs gotten'
    pool_ids = get_pool_ids()
    for i in flickr_ids:
        photo_data = flickr.photos.getInfo(photo_id=flickr_id)
        data = untangle.parse(photo_data)
        for description in data.rsp.photo.description:
            photo_description = description.cdata
            dnz_id = find_dnz_id(photo_description)
            if dnz_id:
                print dnz_id
                test_photo(dnz_id, pool_ids)
            else:
                with open('nonatlibrecord.txt', 'a') as f:
                    f.write("https://www.flickr.com/photos/nationallibrarynz_commons/%r\n" % int(i))
                    f.close()
        n += 1
        time.sleep(0.2)
    print 'Upload to flickr list ready'

def find_dnz_id(description):
    try:
        natlib_url = re.search('(?P<url>https?://[^"]+)', description).group("url")
        if '/records/' in natlib_url:
            dnz_id = natlib_url[-8:]
            return dnz_id
        else:
            return False
    except:
        return False

def test_photo(dnz_id, pool_ids):
    if int(dnz_id) in pool_ids:
        print "YAY"
    else:
        IE_number = get_IE_number(dnz_id)
        with open('uploadtoflickr.txt', 'a') as f:
            f.write("%s\n" % IE_number)
            f.close()

def get_IE_number(dnz_id):
    api_url = 'http://api.digitalnz.org.nz/v3/records/%s.json?api_key=%s&fields=dc_identifier' % (str(dnz_id), dnz_api_key)
    response = requests.get(api_url).json()
    for i in response['record']['dc_identifier']:
        if 'ndha' in i:
            id_string = i
            IE_number = id_string[7:]
            return IE_number
        else:
            return None

def main():
    introduction()
    check_auth()
    create_free_download_list()
    print 'Free downloads listed'
    get_photo_info()

def introduction():
    print '''
This script creates a list of free download images that aren't on Flickr.
When it's finished running, ask NDHA to provide .tif files using the IE
numbers you've gathered in uploadtoflickr.txt.

When you have those, run flickr.py to upload the images and their metadata.
Good hunting!
    '''

main()