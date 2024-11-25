#          Copyright Jean Pierre Cimalando 2022.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE or copy at
#          http://www.boost.org/LICENSE_1_0.txt)
#
# SPDX-License-Identifier: BSL-1.0

import importlib.resources
import os
import sys

from argparse import ArgumentParser, Namespace
from typing import Optional, TextIO, List, Dict
from tempfile import NamedTemporaryFile
from contextlib import ExitStack

from .call_faust import FaustResult, FaustVersion, call_faust, ensure_faust_version, get_faust_version
from .fixes import add_namespace, apply_workarounds, lift_structs, remove_preamble_and_epilog
from .metadata import Metadata, extract_metadata
from .render import render_metadata


class CmdArgs:
    tmplfile: str
    outfile: Optional[str]
    dspfile: str
    classname: str
    lang: str
    defines: Dict[str, str]
    faustargs: List[str]

class CmdError(Exception):
    pass


def main(args=sys.argv):
    with ExitStack() as cleanup_stack:
        cmd: CmdArgs = do_cmdline(args)

        faust_version: FaustVersion = get_faust_version()
        ensure_faust_version(FaustVersion(0, 9, 85), faust_version)

        with NamedTemporaryFile("w", suffix=".cpp" if cmd.lang == "cpp" else ".c") as mdfile:
            if cmd.lang == "cpp":
                mdfile.write("<<<<BeginFaustClass>>>>\n")

            mdfile.write("// END PREAMBLE\n")
            mdfile.write("// START INTRINSICS\n")
            mdfile.write("<<includeIntrinsic>>\n")
            mdfile.write("// END INTRINSICS\n")
            mdfile.write("// START CLASS CODE\n")
            mdfile.write("<<includeclass>>\n")
            mdfile.write("// END CLASS CODE\n")
            mdfile.write("// START EPILOG\n")

            if cmd.lang == "cpp":
                mdfile.write("<<<<EndFaustClass>>>>\n")

            mdfile.flush()

            mdargs: List[str] = ["-a", mdfile.name, "-cn", cmd.classname]

            if cmd.faustargs:
                for arg in cmd.faustargs:
                    try:
                        arg, val = arg.split(" ", 1)
                    except ValueError:
                        val = None

                    if arg in ("-a", "-A", "-cn", "-h", "-o", "-O", "-json",
                               "-lang", "-mdoc", "-ps", "-svg", "-v", "-xml"):
                        continue

                    mdargs.append(arg)

                    if val is not None:
                        mdargs.append(val)

            mdresult: FaustResult = call_faust(cmd.dspfile, mdargs, lang=cmd.lang)

            md: Metadata = extract_metadata(mdresult.docmd)
            md.faustversion = str(faust_version)

            if cmd.lang == "cpp":
                source = apply_workarounds(mdresult.source, mdresult.docmd)
                md.classcode = add_namespace(source)
            elif cmd.lang == "c":
                source, md.structs = lift_structs(mdresult.source)
                md.classcode = remove_preamble_and_epilog(source)

            md.source = mdresult.source

        md.filename = os.path.basename(cmd.dspfile)

        success = False

        out: TextIO
        if cmd.outfile is None:
            out = sys.stdout
        else:
            out = open(cmd.outfile, "w")

        def out_cleanup():
            if not success and cmd.outfile is not None:
                os.unlink(cmd.outfile)
        cleanup_stack.callback(out_cleanup)

        tmplfile : str = find_template_file(cmd.tmplfile)
        render_metadata(out, md, tmplfile, cmd.defines)

        out.flush()

        success = True


def do_cmdline(args: List[str]) -> CmdArgs:
    parser: ArgumentParser = ArgumentParser(description="A post-processor for the faust compiler")
    parser.add_argument("-a", "--template", metavar="FILENAME", dest="tmplfile", help="architecture template file")
    parser.add_argument("-c", "--class-name", metavar="IDENT", default="mydsp", help="name of the dsp class/struct (default: %(default)r)")
    parser.add_argument("-l", "--lang", choices=["c", "cpp"], default="cpp", help="language to generate code for (default: %(default)s)")
    parser.add_argument("-o", "--output", dest="outfile", metavar="PATH", help="output file")
    parser.add_argument("-D", "--define", dest="defines", metavar="NAME=VAL", action="append", help="template context variable definition, in the form name=value")
    parser.add_argument("-X", "--faustarg", dest="faustargs", metavar="ARG", action="append", help="extra faust compiler argument")
    parser.add_argument("dspfile", help="source file")

    result: Namespace = parser.parse_args(args[1:])

    if result.tmplfile is None:
        raise CmdError("No architecture file has been specified.\n")

    cmd = CmdArgs()

    cmd.tmplfile = result.tmplfile
    cmd.outfile = result.outfile
    cmd.dspfile = result.dspfile
    cmd.lang = result.lang
    cmd.classname = result.class_name
    cmd.defines = {}
    cmd.faustargs = result.faustargs

    if result.defines is not None:
        defi: str
        for defi in result.defines:
            try:
                idx: int = defi.index("=")
            except ValueError:
                raise CmdError("The definition is malformed.\n")
            cmd.defines[defi[:idx]] = defi[idx+1:]

    return cmd


def find_template_file(name: str) -> str:
    # if missing, search in package resources
    if not os.path.isfile(name):
        pkgname : str = __name__.split(".", 1)[0]
        with importlib.resources.path(pkgname, "architectures") as arcdir:
            path : str = os.path.join(arcdir, name)
            if os.path.isfile(path):
                return path
    # or return the path as it is
    return name
