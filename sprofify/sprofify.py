#!/usr/bin/env python3

import spotipy
import spotipy.util
import sys
import json
import requests
from sprofify import options
from rofi import Rofi

from sprofify.album import Album
from sprofify.artist import Artist

from sprofify.mpc import add_to_queue
from sprofify.mpc import clear_queue


def get_authorization_headers(username):
    f = open(".cache-{}".format(username), "r")
    resultado = json.load(f)

    token = resultado["access_token"]

    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token),
    }


def get_api_dict(username, client_id, client_secret):
    return {
        "username": username,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": "http://localhost:8888",
        "scope": "user-library-read user-read-playback-state user-modify-playback-state",
    }


def get_spotify_client(username, client_id, client_secret):

    api = get_api_dict(username, client_id, client_secret)

    token = spotipy.util.prompt_for_user_token(**api)
    if not token:
        print("Error: token not received", file=sys.stderr)
        sys.exit(1)

    return spotipy.Spotify(auth=token)


def get_device_id(device_type, username):
    response = requests.get(
        "https://api.spotify.com/v1/me/player/devices",
        headers=get_authorization_headers(username),
    )

    for device in response.json()["devices"]:
        if device["type"].casefold() == device_type.casefold():
            return device["id"]


def get_artists_name(name):
    results = sp.search(q=str(name), type="artist")
    items = results["artists"]["items"]
    artists = []

    i = 0
    for artist in items:
        blah = Artist(++i, artist["name"], artist["uri"])
        print(blah)
        artists.append(blah)
    return artists


def get_album_tracks(uri):
    album_tracks = "[ "

    results = sp.album_tracks(uri)

    items = results["items"]

    for idx, track in enumerate(items, start=1):
        album_tracks += '"' + track["uri"] + '"'
        if idx != len(items):
            album_tracks += ", "

    album_tracks += " ]"

    return album_tracks


def get_album_tracklist(uri):
    album_tracks = list()

    results = sp.album_tracks(uri)

    items = results["items"]

    for st in items:
        album_tracks.append(st["uri"])

    return album_tracks


def get_artist_albums(uri):
    results = sp.artist_albums(uri, album_type="album")
    artist_albums = []
    albums = results["items"]
    while results["next"]:
        results = sp.next(results)
        albums.extend(results["items"])
    seen = set()
    albums.sort(key=lambda album: album["name"].lower())
    i = 0
    for album in albums:
        name = album["name"]
        if name not in seen:
            seen.add(name)
            blah = Album(++i, name, album["uri"])
            artist_albums.append(blah)
    return artist_albums


if __name__ == "__main__":

    opt = options.get_options()

    spotify_auth_args = {
        "username": opt.username,
        "client_id": opt.client_id,
        "client_secret": opt.client_secret,
    }

    sp = get_spotify_client(**spotify_auth_args)

    r = Rofi()

    options = ["search", "clear queue"]
    index, key = r.select("select an option", options)

    if key == -1:
        sys.exit(1)

    if index == 1:
        clear_queue()
        sys.exit(1)

    name = r.text_entry("Enter the search term")
    artists = get_artists_name(name)
    selected_artist_idx, selected_artist_key = r.select(
        "Search results", [b.artist_name for b in artists]
    )

    if selected_artist_key == -1:
        sys.exit(1)

    print(artists[selected_artist_idx].artist_name)

    artist_albums = get_artist_albums(artists[selected_artist_idx].spotify_uri)

    selected_album_idx, selected_album_key = r.select(
        "Choose the album", [c.album_name for c in artist_albums]
    )

    if selected_album_key == -1:
        sys.exit(1)

    print(artist_albums[selected_album_idx].spotify_uri)

    track_uri = get_album_tracklist(artist_albums[selected_album_idx].spotify_uri)

    for i in track_uri:
        add_to_queue(i)
#    response = requests.put(
#        'https://api.spotify.com/v1/me/player/play?device_id={}'.format(get_device_id(opt.device_type, opt.username)),
#        headers=get_authorization_headers(opt.username),
#        data='{"uris": ' + track_uri + '}')
