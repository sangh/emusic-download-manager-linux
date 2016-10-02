#!/usr/bin/env python3
"""Emusic Download Manager, NOT (it just downloads everything w/o a GUI).

This script takes two arguments, the first being the directory to download
to (a directory of the artist and the album inside of it are created under
the given directory); and the second argument is the emx file.

First the emx file is parsed and everything to be downloaded is collected,
then any non-existent directories are created and then any files that exist
(based on the given name) are skipped and the rest are downloaded.

This could be made more flexible, but so far it does what I need it to.
"""

import xmltodict
import sys
import os
import urllib

def prn(str_to_print):
    """Wrap print because we need an unbuffered output (b/c we print a status
    as a file is being downloaded).  So we pass `flush`, `end`, and `file`
    to print every time."""

    print(str_to_print, end='', flush=True, file=sys.stderr)

def escape_file_name(name):
    """No filesystems can handle a null or a slash in a file or directory
    name so we replace those with a string saying what it is.  Note that
    any names with any other (unicode) characters will still be preserved in
    the file name which may nor may not cause you problems."""

    return name.replace("\x00", "[null]").replace("/", "[slash]")


if 3 != len(sys.argv):
    prn("Must get exactly two arguments:  a directory and the emx file.\n")
    sys.exit(1)

base_dir = sys.argv[1]
emx_file = sys.argv[2]

if not os.path.isdir(base_dir):
    prn("Not a directory: " + base_dir + "\n")
    sys.exit(1)

with open(emx_file, "rb") as f:
    emx = xmltodict.parse(f)

# I am kind of paranoid about the format b/c Emusic is likely to change it
# whenever they feel like so if anything is unexpected I want to fail.
emx = emx['PACKAGE']

if emx['ACTION'] != "download":
    prn("Package is not for downloads?\n")
    sys.exit(1)

prn("Links Expiration: " + emx['EXP_DATE'] + "\n")

emx = emx['TRACKLIST']

# So if there is only one track (like a single song instead of an album) the
# 'TRACK' key returns an ordered dict, if this emx is an album then the
# 'TRACK' key returns a list of ordered dicts.
emx = emx['TRACK']
if not isinstance(emx, type([])):
    emx = [emx, ]

# So far everything I've seen from Emusic has the same values in each track
# for disc count, album art, artist, and album, make sure they are all the
# same and fail if not (which would require changing this script).
# Also check that the mime type and extension are what we want, though if
# something else came through I'd likely just want to download it too.
# You would think that in compilations and multi-disc sets the artists for
# each track would be listed since each track has its own artist node, but it
# isn't.  Emusic puts "Various Artists" as the artist on every track, sigh.
# That means you likely need to get the information from the website and store
# it and there is an album URL in the emx file, but alas that URL is not
# routable on the internet (maybe it's routable within Emusic, who knows?).
disc_count = emx[0]['DISCCOUNT']
if 'ALBUMARTLARGE' in emx[0]:
    album_art_url = emx[0]['ALBUMARTLARGE']
else:
    album_art_url = emx[0]['ALBUMART']
album = emx[0]['ALBUM']
artist = emx[0]['ARTIST']
file_ext = ".mp3"
for t in emx:
    if t['MIMETYPE'] != 'audio/mpeg':
        prn("Incorrect mime type (" + t['MIMETYPE'] + ").\n")
        sys.exit(1)
    if t['EXTENSION'] != file_ext:
        prn("Incorrect extension (" + t['EXTENSION'] + ").\n")
        sys.exit(1)
    if 'ALBUMARTLARGE' in t:
        art_key = 'ALBUMARTLARGE'
    else:
        art_key = 'ALBUMART'
    if t[art_key] != album_art_url:
        prn("Multiple album art links.\n")
        sys.exit(1)
    if t['ALBUM'] != album:
        prn("Multiple names for the album.\n")
        sys.exit(1)
    if t['ARTIST'] != artist:
        prn("Multiple artists.\n")
        sys.exit(1)


album = escape_file_name(album)
artist = escape_file_name(artist)

out_dir = os.path.join(base_dir, artist, album)
prn("Output directory: " + out_dir + "\n")

# Loop through collecting everything to make sure all elements are there
# and there are no other problems before doing anything to the filesystem.
# This is a list of tuples where each tuple is (url, file_name).
to_download = []

cover_file_name = os.path.join(out_dir, "cover-front.jpg")
if os.path.exists(cover_file_name):
    prn("Skipping: " + cover_file_name + "\n")
else:
    to_download.append((album_art_url, cover_file_name, ))

for t in emx:
    # Construct the file name, which has the artist and album because that
    # is what the old download manager did.
    # Only include the disc count if there is more than one disc.
    # This format is what the original download manager did, but it is kind
    # of redundant.  Perhaps I'll have an option to this script to store it
    # with a different format, with the track number first, maybe even include
    # the length or something.
    track_file_name = artist + "_" + album
    if disc_count != "1":
        track_file_name = track_file_name + "_" + t['DISCNUM']
    track_file_name = track_file_name + "_" + t['TRACKNUM']
    track_file_name = track_file_name + "_" + escape_file_name(t['TITLE'])
    track_file_name = track_file_name + file_ext
    track_file_name = os.path.join(out_dir, track_file_name)

    if os.path.exists(track_file_name):
        prn("Skipping: " + track_file_name + "\n")
    else:
        to_download.append((t['TRACKURL'], track_file_name, ))

os.makedirs(out_dir, exist_ok=True)

def prn_prog(nb, szb, sztot):
    """Download function callback to display progress.
    This might say it got more than 100 % sometimes because it calculates
    the size by multiplying the number of blocks by the block size, but the
    last block may not be a full block size, so the calculated total could be
    more than the total real size."""
    szp = int(nb) * int(szb)
    per = 100.0 * float(szp) / float(sztot)
    prn("\r%15d of %15d (%3.0f %%) so far." % (szp, int(sztot), per))

for d in to_download:
    prn("Getting: " + d[1] + "\n")
    urllib.request.urlretrieve(d[0], d[1], prn_prog)
    prn("\n")
