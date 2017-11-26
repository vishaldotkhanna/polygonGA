from dropbox import Dropbox
from dropbox.files import WriteMode


ACCESS_TOKEN = ''
LOCAL_BASE_PATH = '' #'img_generate_heroku/'
DROPBOX_BASE_PATH = '/polygon_ga_out_4/'
db = Dropbox(ACCESS_TOKEN)


def upload_file(title, use_base_path=True):
    print 'Uploading {} at {}'.format(title, DROPBOX_BASE_PATH)
    path = LOCAL_BASE_PATH + title if use_base_path else title
    with open(path, 'rb') as f:
        response = db.files_upload(f.read(), DROPBOX_BASE_PATH + title, mode=WriteMode('overwrite'))


if __name__ == '__main__':
    upload_file(title='')
