#          Copyright Jean Pierre Cimalando 2022.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE or copy at
#          http://www.boost.org/LICENSE_1_0.txt)
#
# SPDX-License-Identifier: BSL-1.0

import re
import os
import sys
import xml.etree.ElementTree as ET

from subprocess import run, CompletedProcess, PIPE
from tempfile import TemporaryDirectory
from typing import Optional, List, Dict

from .fixes import apply_workarounds

class FaustVersion:
    maj: int
    min: int
    pat: int

    def __init__(self, maj: int, min: int, pat: int):
        self.maj = maj
        self.min = min
        self.pat = pat

    def __lt__(self, other: 'FaustVersion'):
        return (self.maj, self.min, self.pat) < (other.maj, other.min, other.pat)

    def __str__(self):
        return '%d.%d.%d' % (self.maj, self.min, self.pat)

FAUST_COMMAND_: Optional[str] = None

def get_faust_command() -> str:
    global FAUST_COMMAND_
    cmd: Optional[str] = FAUST_COMMAND_
    if cmd is None:
        cmd = os.getenv('FAUST')
        if cmd is None:
            cmd = 'faust'
        FAUST_COMMAND_ = cmd
    return cmd

def get_faust_version() -> FaustVersion:
    cmd: List[str] = [get_faust_command(), '--version']
    proc: CompletedProcess = run(cmd, stdout=PIPE)
    proc.check_returncode()

    reg = re.compile(r'(\d+)\.(\d+).(\d+)')
    mat = reg.search(proc.stdout.decode('utf-8'))
    if mat is None:
        raise ValueError('Cannot extract the version of faust.')

    ver = FaustVersion(int(mat.group(1)), int(mat.group(2)), int(mat.group(3)))
    return ver

class FaustVersionError(Exception):
    pass

def ensure_faust_version(minver: FaustVersion, ver: Optional[FaustVersion] = None):
    if ver == None:
        ver = get_faust_version()

    if ver < minver:
        msg = "The Faust version %s is too old, the requirement is %s.\n" % (ver, minver)
        raise FaustVersionError(msg)

class FaustResult:
    source: str
    docmd: ET.ElementTree

def call_faust(dspfile: str, faustargs: List[str], lang: str = "cpp") -> FaustResult:
    workdir = TemporaryDirectory()

    dspfilebase = os.path.basename(dspfile)
    xmlfilebase = dspfilebase + ".xml"
    srcfilebase = dspfilebase + "." + lang
    xmlfile = os.path.join(workdir.name, xmlfilebase)
    srcfile = os.path.join(workdir.name, srcfilebase)

    fargv: List[str] = [
        get_faust_command(),
        "-O", workdir.name,
        "-o", srcfilebase,
        "-xml",
        "-lang", lang,
    ] + faustargs

    proc: CompletedProcess = run(fargv + [dspfile])
    proc.check_returncode()

    source = open(srcfile, 'r').read()
    docmd = ET.parse(xmlfile)

    result = FaustResult()
    result.source = source
    result.docmd = docmd
    return result
