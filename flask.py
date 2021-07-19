from flask import Flask, request, render_template
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from itertools import permutations

client_id = ''
client_secret = ''

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
  
def createLList(fullstr): # creates linked list of words in string
    words = fullstr.split(' ') # split string into individual words
    head = Link(words[0]) # head = first word
    ptr = head
    
    for i in range(1,len(words)): # assemble linked list from word array
        ptr.next = Link(words[i])
        ptr = ptr.next

    return head     

def assemblePossibleSongsDict(head,sp): # assembles dictionary of valid songs from substrings present on linked list
    possible = {}
    ptr = head
    while (ptr != None): # loops through for every word 
        str = ""
        ptr2 = ptr
        while (ptr2 != None): # loops through for every word after current word in first loop
            str += ptr2.content + " " # appends to combination
            if (song := searchSongs(str.strip(),sp)): # if valid song name, add to dict w/ song uri 
                possible[song["name"]] = song["uri"]
            ptr2 = ptr2.next
        ptr = ptr.next
    return possible # returns dictionary of valid song substrings

def assembleSongCombos(songlist, fullstr): # assembles combinations of valid song substrings until it finds an exact match of full string
    for i in range(1, len(songlist)+1): # make all possible i length permutations
        combs = permutations(songlist,i)
        for comb in combs:
            str = ""
            for words in comb: # adds all words in combination
                str += words + " "
                if (str.strip() == fullstr): # checks if match
                    return comb # returns working combination of songs if matches
            
def assembleListOfIDs(songdict, combo): # assembles into list of uris for playlist addition
    songs = []
    for song in combo:
        songs.append(songdict[song])
    return songs
        
class Link: # link for linked list
    def __init__(self, content):
        self.content = content
        self.next = None

app = Flask(__name__)

@app.route("/", methods = ["GET", "POST"])
def index():
    if request.method == "POST":
       # getting input from HTML form
        string = request.form.get("string")
        username = request.form.get("name")

        # doing search & assembly
        sp = login(username) # logs into spotify
        llist = createLList(string) # creates linked list from string
        poss_songs = assemblePossibleSongsDict(llist,sp) # assembles possible song combinations
        if (combos := assembleSongCombos(poss_songs, string)): # if valid combo exits, success, form playlist
            listOfIDs = assembleListOfIDs(poss_songs, combos) # gathers ids of valid combo into list
            pid = createSpotifyPlaylist(username, string, sp) # creates playlist
            addSongsToPlaylist(username, pid, listOfIDs, sp) # adds songs to playlist
            return render_template("form_success.html")
        else: # valid combo doesn't exist, failure, retry
            return render_template("form_failure.html")
    return render_template("form.html")

if __name__=='__main__':
    app.run(host="127.0.0.1", port=8080, debug=True, use_reloader=False)

