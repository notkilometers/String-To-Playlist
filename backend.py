from itertools import combinations
import spotipy

client_id = '' # put spotify client id here
client_secret = '' # put spotify client secret here 
username = '' # put spotify username here

token = spotipy.util.prompt_for_user_token(username,scope="playlist-modify-public user-library-modify",client_id=client_id,client_secret=client_secret,redirect_uri="http://localhost:8080/callback") # login w/ playlist and library perms
sp = spotipy.Spotify(auth=token)

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
