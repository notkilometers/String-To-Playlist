from flask import Flask, request, render_template
from itertools import combinations
import spotipy

client_id = '' # put spotify client id here
client_secret = '' # put spotify client secret here

def login(username):
    token = spotipy.util.prompt_for_user_token(username,scope="playlist-modify-public user-library-modify",client_id=client_id,client_secret=client_secret,redirect_uri="http://localhost:8080/callback") # login w/ playlist and library perms
    sp = spotipy.Spotify(auth=token)
    return sp

def searchSongs(name, sp): # returns spotify songs with exact matching name
    results = sp.search(type='track', limit='50', q=name)["tracks"]["items"]  # queries spotify for song results 
    for song in results: # iterates through all songs in result
        if (name == song["name"]): # if song name is exact match with requested song name
            return song

def createSpotifyPlaylist(username, name, sp): # makes playlist with passed name, returns created playlist's id
    playlist = sp.user_playlist_create(username, name=name)
    return playlist["id"]

def addSongsToPlaylist(username, playID, songIDs, sp): # adds songs in list to playlist
    sp.user_playlist_add_tracks(username, playlist_id=playID, tracks=songIDs)   

def assemblePossibleSongsDict(fullstr,sp): # assembles dictionary of valid songs
    possible = {} 
    words = fullstr.split(' ') # splits string into array of words
    length = len(words)

    for i in range(0,length): # loops through for every word 
        str = ""
        for j in range(i,length): # loops through for every word after and including current word in first loop
            str += (" " + words[j]) if (str != "") else (words[j]) # appends to string, with leading space only if not empty string
            if (song := searchSongs(str, sp)): # if valid song name, add to dict w/ song uri
                possible[song["name"]] = song["uri"]
                
    return possible # returns dictionary of valid song substrings

def assembleSongCombos(songlist, fullstr): # assembles combinations of valid song substrings until it finds an exact match of full string
    for i in range(1, len(songlist)+1): # make all possible i length combinations
        combs = combinations(songlist,i)
        for comb in combs:
            str = " ".join(comb) # join all words in combination to string
            if (str == fullstr): # checks if match
                return comb # returns working combination of songs if matches
            
def assembleListOfIDs(songdict, combo): # assembles into list of uris for playlist addition
    songs = []
    for song in combo:
        songs.append(songdict[song]) # appends uri from dict to list, ordered SA the string
    return songs

app = Flask(__name__)

@app.route("/", methods = ["GET", "POST"])
def index():
    if request.method == "POST":
       # getting input from HTML form
        string = request.form.get("string")
        username = request.form.get("name")

        # doing search & assembly
        sp = login(username) # logs into spotify
        poss_songs = assemblePossibleSongsDict(string,sp) # assembles possible song combinations
        if (combo := assembleSongCombos(poss_songs, string)): # if valid combo exits, success, form playlist
            listOfIDs = assembleListOfIDs(poss_songs, combo) # gathers ids of valid combo into list
            pid = createSpotifyPlaylist(username, string, sp) # creates playlist
            addSongsToPlaylist(username, pid, listOfIDs, sp) # adds songs to playlist
            return render_template("form_success.html")
        else: # valid combo doesn't exist, failure, retry with new string
            return render_template("form_failure.html")
    return render_template("form.html") # base form loaded on get req

if __name__=='__main__':
    app.run(host="127.0.0.1", port=8080, debug=True, use_reloader=False)

