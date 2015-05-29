import requests, untangle, re, time

flickr_api_key = '9f7394f66ebf9610691621ab5cfc000a'
flickr_secret_key = '0d7046e5aab3ca16'

flickr_base_url = 'https://api.flickr.com/services/rest/?method='
photo_list_method = 'flickr.people.getPhotos'
photo_method = 'flickr.photos.getInfo'

def get_pool_ids():
    all_ids = []
    with open('atl_numbers.txt', 'r') as f:
        for line in f:
            number = int(line)
            all_ids.append(number)
    return all_ids

def get_flickr_ids():
    all_flickr_ids = []
    data = untangle.parse('photostream.xml')
    for photo in data.rsp.photo:
        photo_id = photo['id']
        all_flickr_ids.append(photo_id)
    return all_flickr_ids

def get_photo_info():
    n = 1
    all_flickr_ids = get_flickr_ids()
    all_ids = get_pool_ids()
    for i in all_flickr_ids:
        request_url = build_flickr_request(str(i))
        data = untangle.parse(request_url)
        for description in data.rsp.photo.description:
            photo_description = description.cdata
            natlib_id = find_natlib_id(photo_description)
            if natlib_id:
                print natlib_id
                test_photo(natlib_id, all_ids)
            else:
                with open('nonatlibrecord.txt', 'a') as f:
                    f.write("https://www.flickr.com/photos/nationallibrarynz_commons/%r\n" % int(i))
                    f.close()
        print n
        n += 1
        time.sleep(0.2)
    remaining_images(all_ids)

def build_flickr_request(photo_id):
    request_url = flickr_base_url + photo_method + '&api_key=' + flickr_api_key + '&photo_id=' + photo_id
    return request_url

def find_natlib_id(description):
    try:
        natlib_url = re.search('(?P<url>https?://[^"]+)', description).group("url")
        if '/records/' in natlib_url:
            natlib_id = natlib_url[-8:]
            return natlib_id
        else:
            return False
    except:
        return False

def test_photo(natlib_id, all_ids):
    if int(natlib_id) in all_ids:
        print "YAY"
        with open('imagesinboth.txt', 'a') as f:
            f.write("http://natlib.govt.nz/records/%r\n" % int(natlib_id))
            f.close()
        all_ids.remove(int(natlib_id))
    else:
        with open('flickrcommons.txt', 'a') as f:
            f.write("http://natlib.govt.nz/records/%r\n" % int(natlib_id))
            f.close()

def remaining_images(all_ids):
    for i in all_ids:
        with open('freedownloads.txt', 'a') as f:
            f.write("http://natlib.govt.nz/records/%r\n" % int(i))
            f.close()

get_photo_info()