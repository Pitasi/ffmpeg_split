#!/usr/bin/env python
import os
import re
import pprint
import sys
import subprocess as sp
from os.path import basename
from subprocess import *
from optparse import OptionParser

def parseChapters(filename):
  chapters = []
  command = [ "ffmpeg", '-i', filename]
  output = ""
  m = None
  title = None
  chapter_match = None
  try:
    # ffmpeg requires an output file and so it errors
    # when it does not get one so we need to capture stderr,
    # not stdout.
    output = sp.check_output(command, stderr=sp.STDOUT, universal_newlines=True)
  except CalledProcessError, e:
    output = e.output

  num = 1

  for line in iter(output.splitlines()):
    x = re.match(r".*title.*: (.*)", line)
    print "x:"
    pprint.pprint(x)

    print "title:"
    pprint.pprint(title)

    if x == None:
      m1 = re.match(r".*Chapter #(\d+:\d+): start (\d+\.\d+), end (\d+\.\d+).*", line)
      title = None
    else:
      title = x.group(1)

    if m1 != None:
      chapter_match = m1

    print "chapter_match:"
    pprint.pprint(chapter_match)

    if title != None and chapter_match != None:
      m = chapter_match
      pprint.pprint(title)
    else:
      m = None

    if m != None:
      chapters.append({ "num": num, "title": title, "start": m.group(2), "end": m.group(3)})
      num += 1

  return chapters

def getChapters():
  parser = OptionParser(usage="usage: %prog [options] filename", version="%prog 1.0")
  parser.add_option("-f", "--file",dest="infile", help="Input File", metavar="FILE")
  (options, args) = parser.parse_args()
  if not options.infile:
    parser.error('Filename required')
  chapters = parseChapters(options.infile)
  fbase, fext = os.path.splitext(options.infile)
  path, file = os.path.split(options.infile)
  newdir, fext = os.path.splitext( basename(options.infile) )

  os.mkdir(path + "/" + newdir)

  leading_zeros_size = len(str(len(chapters)))
  for chap in chapters:
    chap['title'] = chap['title'].replace('/',':')
    chap['title'] = chap['title'].replace("'","\'")
    print "start:" +  chap['start']
    
    outfilename = str(chap['num']).zfill(leading_zeros_size) + ' - ' + chap['title']
    chap['outfile'] = path + "/" + newdir + "/" + re.sub("[^-a-zA-Z0-9_.():' ]+", '', outfilename) + fext
    chap['origfile'] = options.infile
    print chap['outfile']
  return chapters

def convertChapters(chapters):
  for chap in chapters:
    print "start:" +  chap['start']
    print chap
    command = [
        "ffmpeg", '-i', chap['origfile'],
        '-vcodec', 'copy',
        '-acodec', 'copy',
        '-metadata',
          'title='+chap['title'],
        '-metadata',
          'track='+str(chap['num']),
        '-ss', chap['start'],
        '-to', chap['end'],
        chap['outfile']]
    output = ""
    try:
      # ffmpeg requires an output file and so it errors
      # when it does not get one
      output = sp.check_output(command, stderr=sp.STDOUT, universal_newlines=True)
    except CalledProcessError, e:
      output = e.output
      raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

if __name__ == '__main__':
  chapters = getChapters()
  convertChapters(chapters)
