#!/usr/bin/env python2

# Requires python-discid and python-musicbrainzngs

import os
import sys
import json
import discid
import musicbrainzngs as ws

# default options
output = "NORMAL"
device = discid.get_default_device()


# usage function for print help info
def usage():
    fname = os.path.basename(sys.argv[0])
    print("usage: {0:s} [DEVICE] [OPTION]".format(fname))
    print("\t [DEVICE]\t Example: /dev/cdrom")
    print("\t -h\t\t print help information and exit")
    print("\t -j\t\t return results in JSON format")


# read the options from sys.argv
def parseOpts():
    global output, device

    for arg in sys.argv:
        if arg != sys.argv[0]:
            if arg == "-h":
                usage()
                exit(1)
            elif arg == "-j":
                output = "JSON"
            else:
                device = arg


# read properties from the given disc device
def getDisc(device):
    return discid.read(device=device)


# get metadata from musicbrainz api
def getReleases(disc):
    ws.set_useragent("musicbrainz_discid", "0.2")
    includeVars = ["artists", "recordings", "labels"]
    return ws.get_releases_by_discid(disc.id, toc=disc.toc_string, cdstubs=False, includes=includeVars)

# read options, return usage or option variables
parseOpts()

if output != "JSON":
    print("Device: " + device)

# get the disc table of contents
disc = getDisc(device)

if output != "JSON":
    print("Disc ID: " + disc.id)
    print("TOC:     " + disc.toc_string)

# get the artist/album/track info for the disc
r = getReleases(disc)

if "disc" in r and r["disc"]["release-count"] > 0:
    if output != "JSON":
        print("Disc ID found")
    releases = r["disc"]["release-list"]
elif "release-list" in r and len(r["release-list"]) > 0:
    if output != "JSON":
        print("TOC search succeeded")
    releases = r["disc"]["release-list"]
else:
    if output != "JSON":
        print("Release not found")
    else:
        print('{"success":false,"message":"Release not found"}')
    exit(1)

if output == "JSON":
    # print JSON
    print(json.dumps(releases))
else:
    # print plain text

    rnum = 1
    for x in releases:
        print("Release " + str(rnum) + ":")
        print("  ID:     " + x['id'])
        print("  URL:    http://musicbrainz.org/release/" + x['id'])
        print("  Title:  " + x['title'] + " ["
                + (x['release-event-list'][0]['date'] if 'release-event-list' in x and 'date' in x['release-event-list'][0] else "<no date>")
                + ", " + (x['country'] if 'country' in x else "<no country>")
                + ", " + (x['label-info-list'][0]['label']['name'] if x['label-info-count'] > 0 else "<no label>") + "]")
        print("  Artist: " + x['artist-credit'][0]['artist']['name'])
        print("  Tracks:")
        for x in x['medium-list']:
            print("    " + (x['format'] if 'format' in x else "Medium") + " " + str(x['position']) + ":")
            tnum = 1
            for x in x['track-list']:
                print("      " + "{0:02d} ".format(tnum) + x['recording']['title'])
            tnum += 1
rnum += 1
