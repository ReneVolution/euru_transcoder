#!/bin/env pyhton

""" Small script to transcode a video using given Profiles. """

import datetime
import json
import logging
import os
import shlex
import sys
import math
import urllib2
from subprocess import Popen, PIPE
from threading import Thread

LOGFILE = "transcode_{0}.log".format(
    datetime.datetime.now().strftime("%Y-%m-%d-%H_%M_%S"))

logging.basicConfig(filename=LOGFILE,
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s')


MP4_CMD = ("ffmpeg -loglevel error -i {src} "
           "-filter_complex scale={width}:{height} "
           "-sws_flags lanczos+accurate_rnd "
           "-c:v libx264 -profile:v {profile} -b:v {v_bitrate}k "
           "-x264opts aud:bframes=3:direct=auto:keyint={gopsize}:level=31:"
           "me=esa:merange=16:min-keyint=1:no-fast-pskip:no-mbtree:"
           "no-mixed-refs:nr=1000:"
           "partitions=+parti8x8+parti4x4+partp8x8+partp4x4:qcomp=0.7:"
           "qpmax=51:qpmin=10:ratetol=0.1:rc-lookahead=40:scenecut=40:"
           "subme=7:trellis=2:weightp=2 "
           "-force_key_frames 'expr:gte(n,n_forced*{gopsize})' "
           "-c:a libfdk_aac -b:a {a_bitrate}k -ar 48000 -ac 2 "
           "-movflags +faststart -pass {passno} -passlogfile {tplog} "
           "-f mp4 -y {outname}")


HLS_CMD = ("ffmpeg -loglevel error -i {src} -c copy -map 0 "
           "-bsf:v h264_mp4toannexb -bsf:a aac_adtstoasc -flags global_header "
           "-f segment -segment_time 10 -segment_list {seglist_name} "
           "-segment_list_type m3u8 -segment_format mpegts {outname}")


WEBM_CMD = ("ffmpeg -loglevel error -i {src} "
            "-filter_complex scale={width}:{height} "
            "-sws_flags lanczos+accurate_rnd "
            "-c:v vp8 -g {gopsize} -cpu-used 0 -deadline realtime -qmin 0 "
            "-qmax 63 -bufsize {bufsize}k -maxrate {v_bitrate}k "
            "-arnr-maxframes 7 -arnr-strength 5 -arnr-type centered "
            "-auto-alt-ref 1 -c:a libvorbis -b:a {a_bitrate}k -ar 48000 "
            "-pass {passno} -passlogfile {tplog} -f webm -y {outname}")


def execute(cmd, src_fname, dst_fname):
    logging.info("Started to transcode file: {0} => {1}".format(
        src_fname, dst_fname))

    p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
    __, stderr = p.communicate()

    logging.info("Finished transcoding of file: {0} => {1}".format(
        src_fname, dst_fname))


def fetch_from_http(url):
    baseFile = "".join(x for x in os.path.basename(url) if x.isalnum())

    temp_path = "/tmp/"
    try:
        file = os.path.join(temp_path, baseFile)

        req = urllib2.urlopen(url)
        total_size = int(req.info().getheader('Content-Length').strip())
        downloaded = 0
        CHUNK = 256 * 10240
        with open(file, 'wb') as fp:
            while True:
                chunk = req.read(CHUNK)
                downloaded += len(chunk)
                print math.floor((downloaded / total_size) * 100)
                if not chunk:
                    break
                fp.write(chunk)
    except urllib2.HTTPError, e:
        print "HTTP Error:", e.code, url
        return False
    except urllib2.URLError, e:
        print "URL Error:", e.reason, url
        return False

    return file


def process(src_fname, destroot, profiles):

    """ Process Source video with both pre-defined settings and
        Settings based on profile. """

    with open(profiles, 'rb') as json_data:
        tasks = []
        enc_profiles = json.loads(json_data.read())
        passno = 1
        src_base = os.path.basename(src_fname).rsplit('.', 1)[0]
        dst_base = os.path.join(destroot, src_base)
        out_base = os.path.join(dst_base, src_base)

        try:
            os.makedirs(dst_base)
        except:
            pass

        while passno <= 2:
            for profile in enc_profiles:
                tplog = "/tmp/twopass_{0}_{1}".format(
                    src_base, profile['postfix'])

                if 'mp4' in profile['type']:
                    if passno == 1:
                        out_fname = '/dev/null'
                    else:
                        out_fname = "{0}_{1}.mp4".format(
                            out_base, profile['postfix'])

                    cmd = MP4_CMD.format(src=src_fname,
                                         width=profile['width'],
                                         height=profile['height'],
                                         profile=profile['profile'],
                                         v_bitrate=profile['video_br'],
                                         a_bitrate=profile['audio_br'],
                                         gopsize=profile['gopsize'],
                                         passno=passno,
                                         tplog=tplog,
                                         outname=out_fname)

                if 'webm' == profile['type'].lower():
                    if passno == 1:
                        out_fname = '/dev/null'
                    else:
                        out_fname = "{0}_{1}.webm".format(
                            out_base, profile['postfix'])
                    bufsize = int(profile['video_br']) * 2
                    cmd = WEBM_CMD.format(src=src_fname,
                                          width=profile['width'],
                                          height=profile['height'],
                                          v_bitrate=profile['video_br'],
                                          a_bitrate=profile['audio_br'],
                                          bufsize=bufsize,
                                          gopsize=profile['gopsize'],
                                          passno=passno,
                                          tplog=tplog,
                                          outname=out_fname)

                t = Thread(target=execute, args=(cmd, src_fname, out_fname))
                t.start()
                tasks.append(t)

            for t in tasks:
                t.join()
            passno += 1

        index_files = []

        for profile in enc_profiles:
            if '+hls' in profile['type']:
                seg_path = os.path.join(dst_base, profile['postfix'])
                try:
                    os.makedirs(seg_path)
                except:
                    pass

                src_fname = "{0}_{1}.mp4".format(
                    out_base, profile['postfix'])
                seg_list = os.path.join(seg_path, 'index.m3u8')
                index_files.append(("{0}/index.m3u8".format(
                    profile['postfix']),
                    profile['video_br'] + profile['audio_br']))
                outname = os.path.join(seg_path, 'segment_%05d.ts')

                cmd = HLS_CMD.format(src=src_fname,
                                     seglist_name=seg_list,
                                     outname=outname)

                t = Thread(target=execute, args=(cmd, src_fname, out_fname))
                t.start()
                tasks.append(t)

            for t in tasks:
                t.join()

        if len(index_files) > 0:
            master_pl = os.path.join(dst_base, 'master.m3u8')
            with open(master_pl, 'wb') as fp:
                fp.write("#EXTM3U\n")
                for ifp in index_files:
                    fp.write(("#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH="
                              "{bw}000\n").format(
                                  bw=ifp[1]))
                    fp.write(ifp[0] + '\n')

if __name__ == '__main__':
    if len(sys.argv) > 2:
        input_file = sys.argv[1]
        destination = sys.argv[2]
        profile_data = sys.argv[3]

        if input_file.startswith("http://"):
            tmpfile = fetch_from_http(input_file)
            if tmpfile is not False:
                process(input_file, destination, profile_data)
        else:
            process(input_file, destination, profile_data)
    else:
        print ("Usage: {0} <Inputfile> <Destination-Path> "
               "<Profile.json>").format(sys.argv[0])
