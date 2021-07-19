import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from itertools import combinations

client_id = ''
client_secret = ''
username = ''

token = spotipy.util.prompt_for_user_token(username,scope="playlist-modify-public user-library-modify",client_id=client_id,client_secret=client_secret,redirect_uri="http://localhost:8080/callback") # login w/ playlist and library perms
sp = spotipy.Spotify(auth=token)

def searchSongs(name): # returns spotify songs with exact matching name
    results = sp.search(type='track', limit='50', q=name)["tracks"]["items"]  # queries spotify for song results 
    for song in results: # iterates through all songs in result
        if (name == song["name"]): # if song name is exact match with requested song name
            return song

def createSpotifyPlaylist(name): # makes playlist with passed name, returns created playlist's id
    playlist = sp.user_playlist_create(username, name=name)
    return playlist["id"]

def addSongsToPlaylist(playID, songIDs): # adds songs in list to playlist
    sp.user_playlist_add_tracks(username, playlist_id=playID, tracks=songIDs)
  
def createLList(fullstr): # creates linked list of words in string
    words = fullstr.split(' ') # split string into individual words
    head = Link(words[0]) # head = first word
    ptr = head
    
    for i in range(1,len(words)): # assemble linked list from word array
        ptr.next = Link(words[i])
        ptr = ptr.next

    return head     

def assemblePossibleSongsDict(head): # assembles dictionary of valid songs from substrings present on linked list
    possible = {}
    ptr = head
    while (ptr != None): # loops through for every word 
        str = ""
        ptr2 = ptr
        while (ptr2 != None): # loops through for every word after current word in first loop
            str += ptr2.content + " " # appends to combination
            if (song := searchSongs(str.strip())): # if valid song name, add to dict w/ song uri 
                possible[song["name"]] = song["uri"]
            ptr2 = ptr2.next
        ptr = ptr.next
    return possible # returns dictionary of valid song substrings

def assembleSongCombos(songlist, fullstr): # assembles combinations of valid song substrings until it finds an exact match of full string
    for i in range(1, len(songlist)+1): # make all possible i length permutations
        combs = combinations(songlist,i)
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
