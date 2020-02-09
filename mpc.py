from subprocess import check_output

"""
mpc class - wrapper to control mpc
shamelessly copied from https://github.com/garyconstable/python-media-player/blob/master/mpc.py
"""


def add_to_queue(track_uri):
    try:
        print("----> Add song - id: {}".format(track_uri))
        check_output("mpc add " + track_uri, shell=True)
    except (RuntimeError, TypeError, NameError):
        pass
