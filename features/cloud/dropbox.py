# import sys
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

# Add OAuth2 access token here.
# You can generate one for yourself in the App Console.
# See <https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account/>

TOKEN = "jLMxq7XJeHUAAAAAAAAAAe3ddfZrPUZqXWvou3GhmmlEGFqvdJYR-_uFXvFSMN4b"

# LOCALFILE = 'tohoerr.png'
# BACKUPPATH = '/toho-err.png'

if (len(TOKEN) == 0):
    print("ERROR: Looks like you didn't add your access token.")

# Create an instance of a Dropbox class, which can make requests to the API.

else:
    print("Creating a Dropbox object...")
    dbx = dropbox.Dropbox(TOKEN)

    # Check that the access token is valid
    try:
        dbx.users_get_current_account()
        
        # Uploads contents of LOCALFILE to Dropbox
        def backup(LOCALPATH, BACKUPPATH):
            with open(LOCALPATH, 'rb') as f:
                # We use WriteMode=overwrite to make sure that the settings in the file
                # are changed on upload
                print("Uploading " + LOCALPATH + " to Dropbox as " + BACKUPPATH + "...")
                try:
                    dbx.files_upload(f.read(), BACKUPPATH, mode=WriteMode('overwrite'))
                except ApiError as err:
                    # This checks for the specific error where a user doesn't have
                    # enough Dropbox space quota to upload this file
                    if (err.error.is_path() and
                            err.error.get_path().reason.is_insufficient_space()):
                        print("ERROR: Cannot back up; insufficient space.")
                    elif err.user_message_text:
                        print(err.user_message_text)
                        # sys.exit()
                    else:
                        print(err)
                        # sys.exit()
                        
        # Look at all of the available revisions on Dropbox, and return the oldest one
        def select_revision(FILEPATH):
            # Get the revisions for a file (and sort by the datetime object, "server_modified")
            print("Finding available revisions on Dropbox...")
            entries = dbx.files_list_revisions(FILEPATH, limit=30).entries
            revisions = sorted(entries, key=lambda entry: entry.server_modified)

            for revision in revisions:
                print(revision.rev, revision.server_modified)

            # Return the oldest revision (first entry, because revisions was sorted oldest:newest)
            return revisions[0].rev

        def download_from_dropbox(LOCALPATH, BACKUPPATH):
            print("Downloading File...")
            entry = dbx.files_download_to_file(LOCALPATH, BACKUPPATH)
            
            return entry
    except AuthError:
        print("ERROR: Invalid access token; try re-generating an " +
            "access token from the app console on the web.")




    # Change the text string in LOCALFILE to be new_content
    # @param new_content is a string
    # def change_local_file(new_content):
    #     print("Changing contents of " + LOCALFILE + " on local machine...")
    #     with open(LOCALFILE, 'wb') as f:
    #         f.write(new_content)

    # Restore the local and Dropbox files to a certain revision
    # def restore(rev=None):
    #     # Restore the file on Dropbox to a certain revision
    #     print("Restoring " + BACKUPPATH + " to revision " + rev + " on Dropbox...")
    #     dbx.files_restore(BACKUPPATH, rev)

    #     # Download the specific revision of the file at BACKUPPATH to LOCALFILE
    #     print("Downloading current " + BACKUPPATH + " from Dropbox, overwriting " + LOCALFILE + "...")
    #     dbx.files_download_to_file(LOCALFILE, BACKUPPATH, rev)



# if __name__ == '__main__':

    # Create a backup of the current settings file
    # backup("./data/db/nandeshiko-database.db", "/nandeshiko-database.db")

    # Change the user's file, create another backup
    # change_local_file(b"updated")
    # backup()

    # Restore the local and Dropbox files to a certain revision
    # to_rev = select_revision("/nandeshiko-database.db")
    # restore(to_rev)
    
    #Download file based on path
    # download_from_dropbox("./data/db/nandeshiko-database.db", "/nandeshiko-database.db")

    # print("Done!")