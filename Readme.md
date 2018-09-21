Deprecated
==========

This project is no longer useful since Emusic changed to a
download-from-a-web-browser model.


Emusic Download Manager for Linux
=================================

Well, not really a "manager", more of a "doer".  For a while there was an
Emusic Download Manager for Linux that was some horrible buggy GUI thing (but
worked), which is no longer available.  It turns out, though, that the emx
files that were handled by it are just XML files that refer to randomly
generated per-user expiring URL~s that can be retrieved directly after the emx
file is downloaded; so this script parses the XML file and directly downloads
the mp3 files (and cover art) from it.  It creates a directory for the artist
and the album.  Unfortunately not all the metadata is available in the emx file
so should likely be taken from the web page.

It is not as flexible as it could be but does get the job done.  It assumes
everything is UTF-8 (including the file names) and is not at all parallel
(which doesn't seem to speed it up all that much (for me) anyway).

The script takes two arguments.  The first argument is a directory to download
to and the second is the emx file.

Inside the given directory a sub-directory for the artist is created if it does
not exist and inside that a directory for the album.  Then any files that do
not exist (but are in the emx file) are downloaded.

That means if a file has an error downloading the partial file need to be
removed from that directory to have this script retry getting it.


Dependencies
------------

Requires at least python3.3 (b/c of the `flush` argument to print), and
[xmltodict](https://github.com/martinblech/xmltodict).  You might be able to
install xmltodict with your package manager, `pip`, or `easy_install`, but if
you want you can also just copy that one py file in that project to the same
directory as `emusic-emx-get.py`.


To-Do
-----

I would like to be able to get the album metadata but the emx file does not
have it and every URL to the album I've seen in an emx is not routable from the
internet (I don't know what Emusic is doing).  So I usually end up getting the
metadata from the web page.

It would be nice if there was a checksum for the downloaded file, but there
isn't.  There is a size, but it doesn't seem to match the real downloaded file
size (which does match the HTML `content-length` field).  If someone can tell
me why 'DATAPORTIONSIZE' is not the file size I would appreciate it.

The file name and directory structure is what the old download manager did, but
it is kind of stupid, so could be made better.  It would be super nice if
Emusic included the artist information for each track of a compilation (instead
of `Various Artists`), but they don't.
