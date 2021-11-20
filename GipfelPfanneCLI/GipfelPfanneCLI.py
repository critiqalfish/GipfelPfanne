import tidalapi
import webbrowser
import pickle
import sys
import os
from time import sleep
from os import listdir

session = tidalapi.Session()

def menu():

    print("\nwhat do you want to do?\n")

    options = ["log in", "backup playlist", "restore playlist", "log out", "quit"]
    functions = {1 : log_in, 2 : select_playlist_and_save_backup, 3 : select_playlist_and_restore_backup, 4 : log_out , 5 : exit_script}

    for i, option in enumerate(options, 1):
        print("[" + str(i) + "] " + option)
    selection = int(input("\nchoose: "))

    functions[selection]()

def first_time_login(link):

    global result_link

    result_link = link.removeprefix("Visit ").removesuffix(" to log in, the code will expire in 300 seconds")
    print("\n-------- LINK (only use this in case your browser does not automatically open it): " + '"' + "https://" + result_link + '" --------')
    webbrowser.open("https://" + result_link)

def log_in():

    try:
        f = open('./login-data/login.pckl', 'rb')
        obj = pickle.load(f)
        f.close()
        session.load_oauth_session(obj[0], obj[1], obj[2], obj[3])

    except:
        session.login_oauth_simple(function=first_time_login)
        obj = [session.session_id, session.token_type, session.access_token, session.refresh_token]
        f = open('./login-data/login.pckl', 'wb')
        pickle.dump(obj, f)
        f.close()

    finally:
        global uid
        uid = session.user.id
        menu()

def select_playlist_and_save_backup():

    try:
        uid = session.user.id
    except:
        print("\n-------- you have to log in first! --------")
        sleep(2)
        menu()

    global playlist_name
    global playlist_id
    global bkp_playlist_file
    global bkp_playlist_name

    playlists = session.get_user_playlists(uid)

    print("\nwhat playlist do you want to backup?\n")
    for i, ps in enumerate(playlists, 1):
        print("[" + str(i) + "] " + ps.name)

    selection = int(input("\nchoose playlist number: ")) - 1
    print()
    playlist_id = playlists[selection].id
    playlist_name = playlists[selection].name

    bkp_playlist_name = playlist_name + " BACKUP"
    bkp_playlist_file = "./backups/" + bkp_playlist_name + ".txt"

    f = open(bkp_playlist_file, "w")
    tracks = session.get_playlist_tracks(playlist_id)
    for track in tracks:
        print("saved: " + str(track.id))
        f.write(str(track.id) + "\n")
    f.close()

    menu()

def select_playlist_and_restore_backup():

    try:
        uid = session.user.id
    except:
        print("\n-------- you have to log in first! --------")
        sleep(2)
        menu()

    files = listdir("./backups")

    print("\nwhat playlist do you want to restore?\n")
    for i, file in enumerate(files, 1):
        print("[" + str(i) + "] " + file)

    selection = int(input("\nchoose playlist number: "))
    rstr_playlist_file = "./backups/" + files[selection - 1]
    rstr_playlist_name = files[selection - 1].removesuffix(".txt")

    session.request('POST','users/%s/playlists' % uid, data={'title': rstr_playlist_name})
    playlists = session.get_user_playlists(uid)
    for playlist in playlists:
        if playlist.name == rstr_playlist_name:
            rstr_playlist_id = playlist.id
        else:
            pass

    f = open(rstr_playlist_file, "r")
    track_id_list = f.readlines()
    f.close()

    to_index = 0
    headers = {'if-none-match' : "*"}
    data = {
        'trackIds' : ",".join(track_id_list),
        'toIndex' : to_index
            }
    session.request('POST', 'playlists/%s/tracks' % rstr_playlist_id, data = data ,headers = headers)
    
    print("")
    print(".", end = "")
    sys.stdout.flush()
    sleep(1)
    print(".", end = "")
    sys.stdout.flush()
    sleep(1)
    print(".", end = "")
    sys.stdout.flush()
    sleep(1)
    print("\n\n-------- done. --------")

    menu()

def log_out():

    try:
        os.remove("./login-data/login.pckl")
        print("\n-------- you are now logged out! --------")
        exit_script()
    except FileNotFoundError:
        print("\n-------- you are not logged in! --------")
        exit_script()

def exit_script():

    print()
    sys.exit()

try:
    f = open('./login-data/login.pckl', 'rb')
    obj = pickle.load(f)
    f.close()
    session.load_oauth_session(obj[0], obj[1], obj[2], obj[3])

except:
    print("\n-------- you should log in first! --------")
    sleep(1.4)
    menu()

else:
    print("\n-------- you automatically got logged in! --------")
    sleep(1.4)
    menu()