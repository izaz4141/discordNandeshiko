
from __future__ import print_function
import httplib2
import os, io

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
from ..cloud import auth
from typing import Optional
# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drivedb'
authInst = auth.auth(SCOPES,CLIENT_SECRET_FILE,APPLICATION_NAME)
credentials = authInst.getCredentials()

http = credentials.authorize(httplib2.Http())
drive_service = discovery.build('drive', 'v3', http=http)

def listFiles(size):
    results = drive_service.files().list(
        pageSize=size,fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print('{0} ({1})'.format(item['name'], item['id']))

def uploadFile(filename,filepath,mimetype, folderId: Optional[str]="None"):
    if folderId == "None":
        file_metadata = {'name': filename}
    else:
        file_metadata = {
            'name' : filename,
            'parents' : [folderId]
        }
    media = MediaFileUpload(filepath,
                            mimetype=mimetype)
    file = drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    print('File ID: %s' % file.get('id'))

def downloadFile(file_id,filepath):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    with io.open(filepath,'wb') as f:
        fh.seek(0)
        f.write(fh.read())

def createFolder(name):
    file_metadata = {
    'name': name,
    'mimeType': 'application/vnd.google-apps.folder'
    }
    file = drive_service.files().create(body=file_metadata,
                                        fields='id').execute()
    print ('Folder ID: %s' % file.get('id'))

def searchFile(query):
    results = drive_service.files().list(
    fields="nextPageToken, files(id, name, kind, mimeType)",q=query).execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
        return []
    else:
        # print('Files:')
        # for item in items:
        #     print(item)
        #     print('{0} ({1})'.format(item['name'], item['id']))
        return items
    
def deleteFile(id):
    try:
        drive_service.files().delete(fileId= id).execute()
    except Exception as exc:
        print(exc)
    
# if __name__ == "__main__":
    #uploadFile('unnamed.jpg','unnamed.jpg','image/jpeg')
    #downloadFile('1Knxs5kRAMnoH5fivGeNsdrj_SIgLiqzV','google.jpg')
    #createFolder('Google')
    # b = drive_service.files()
    # folder_detail = searchFile("name contains 'discordNandeshiko'")
    # file_detail = searchFile("name contains 'nandeshiko-database'")
    # print(file_detail)
    # deleteFile(file_detail[0]["id"])
    # downloadFile(file_detail[0]["id"], "./data/db/nandeshiko-database.db")
    # uploadFile("nandeshiko-database.db", "./data/db/nandeshiko-database.db", "database/db", folder_detail[0]["id"])

