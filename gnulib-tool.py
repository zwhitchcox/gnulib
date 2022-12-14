#!/usr/bin/env python3
#
# Copyright (C) 2002-2022 Free Software Foundation, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

# This program is meant for authors or maintainers which want to import
# modules from gnulib into their packages.

# CODING STYLE for this file and its companions:
# Like PEP 8 <https://peps.python.org/pep-0008/>, except
# - Line length is not limited to 79 characters.
# - Line breaking before or after binary operators? Better before, like in GNU.
# You can use this command to check the style:
#   $ pycodestyle --max-line-length=128 --ignore=E265,W503,E241,E711,E712,E201,E202 gnulib-tool.py pygnulib/*.py


#===============================================================================
# Define global imports
#===============================================================================
import os
import re
import sys
import codecs
import random
import shutil
import argparse
import subprocess as sp
from tempfile import mktemp
from pprint import pprint
from pygnulib import constants
from pygnulib import classes


#===============================================================================
# Define global constants
#===============================================================================
APP = constants.APP
ENCS = constants.ENCS
UTILS = constants.UTILS
MODES = constants.MODES
TESTS = constants.TESTS
compiler = constants.compiler
joinpath = constants.joinpath
isabs = os.path.isabs
isdir = os.path.isdir
isfile = os.path.isfile


#===============================================================================
# Define main part
#===============================================================================
def main():
    # Reset arguments
    mode = None
    destdir = None
    localpath = None
    modcache = None
    verbose = None
    auxdir = None
    modules = None
    avoids = None
    sourcebase = None
    m4base = None
    pobase = None
    docbase = None
    testsbase = None
    tests = None
    libname = None
    lgpl = None
    makefile = None
    libtool = None
    conddeps = None
    macro_prefix = None
    podomain = None
    witness_c_macro = None
    vc_files = None
    dryrun = None
    errors = None

    info = classes.GLInfo()
    parser = argparse.ArgumentParser(
        prog=constants.APP['name'],
        usage='gnulib-tool.py --help',
        add_help=False)

    # Here we list the options in the order they are listed in the --help output.

    # list
    parser.add_argument('--list',
                        dest='mode_list',
                        default=None,
                        action='store_true')
    # find
    parser.add_argument('--find',
                        dest='mode_find',
                        default=None,
                        action='store_true')
    # import
    parser.add_argument('--import',
                        dest='mode_import',
                        default=None,
                        action='store_true')
    # add-import
    parser.add_argument('--add-import',
                        dest='mode_add_import',
                        default=None,
                        action='store_true')
    # remove-import
    parser.add_argument('--remove-import',
                        dest='mode_remove_import',
                        default=None,
                        action='store_true')
    # update
    parser.add_argument('--update',
                        dest='mode_update',
                        default=None,
                        action='store_true')
    # create-testdir
    parser.add_argument('--create-testdir',
                        dest='mode_create_testdir',
                        default=None,
                        action='store_true')
    # create-megatestdir
    parser.add_argument('--create-megatestdir',
                        dest='mode_create_megatestdir',
                        default=None,
                        action='store_true')
    # test
    parser.add_argument('--test',
                        dest='mode_test',
                        default=None,
                        action='store_true')
    # megatest
    parser.add_argument('--megatest',
                        dest='mode_megatest',
                        default=None,
                        action='store_true')
    # extract-*
    parser.add_argument('--extract-description',
                        dest='mode_xdescription',
                        default=None,
                        action='store_true')
    parser.add_argument('--extract-comment',
                        dest='mode_xcomment',
                        default=None,
                        action='store_true')
    parser.add_argument('--extract-status',
                        dest='mode_xstatus',
                        default=None,
                        action='store_true')
    parser.add_argument('--extract-notice',
                        dest='mode_xnotice',
                        default=None,
                        action='store_true')
    parser.add_argument('--extract-applicability',
                        dest='mode_xapplicability',
                        default=None,
                        action='store_true')
    parser.add_argument('--extract-filelist',
                        dest='mode_xfilelist',
                        default=None,
                        action='store_true')
    parser.add_argument('--extract-dependencies',
                        dest='mode_xdependencies',
                        default=None,
                        action='store_true')
    parser.add_argument('--extract-autoconf-snippet',
                        dest='mode_xautoconf',
                        default=None,
                        action='store_true')
    parser.add_argument('--extract-automake-snippet',
                        dest='mode_xautomake',
                        default=None,
                        action='store_true')
    parser.add_argument('--extract-include-directive',
                        dest='mode_xinclude',
                        default=None,
                        action='store_true')
    parser.add_argument('--extract-link-directive',
                        dest='mode_xlink',
                        default=None,
                        action='store_true')
    parser.add_argument('--extract-license',
                        dest='mode_xlicense',
                        default=None,
                        action='store_true')
    parser.add_argument('--extract-maintainer',
                        dest='mode_xmaintainer',
                        default=None,
                        action='store_true')
    # copy-file
    parser.add_argument('--copy-file',
                        dest='mode_copy_file',
                        default=None,
                        action='store_true')
    # help
    parser.add_argument('--help', '--hel', '--he', '--h',
                        dest='help',
                        default=None,
                        action='store_true')
    # version
    parser.add_argument('--version', '--versio', '--versi', '--vers',
                        dest='version',
                        default=None,
                        action='store_true')
    # no-changelog: a no-op for backward compatibility
    parser.add_argument('--no-changelog',
                        dest='changelog',
                        default=None,
                        action='store_false')
    # destdir
    parser.add_argument('--dir',
                        dest='destdir',
                        default=None,
                        nargs=1)
    # localpath
    parser.add_argument('--local-dir',
                        action='append',
                        dest='localpath',
                        default=None,
                        nargs=1)
    # verbose
    parser.add_argument('--verbose',
                        default=0,
                        action='count')
    # quiet
    parser.add_argument('--quiet',
                        default=0,
                        action='count')
    # dryrun
    parser.add_argument('--dry-run',
                        dest='dryrun',
                        default=None,
                        action='store_true')
    # inctests
    parser.add_argument('--with-tests',
                        dest='inctests',
                        default=None,
                        action='store_true')
    # obsolete
    parser.add_argument('--with-obsolete',
                        dest='obsolete',
                        default=None,
                        action='store_true')
    # c++-tests
    parser.add_argument('--with-c++-tests',
                        dest='cxx',
                        default=None,
                        action='store_true')
    # longrunning-tests
    parser.add_argument('--with-longrunning-tests',
                        dest='longrunning',
                        default=None,
                        action='store_true')
    # privileged-tests
    parser.add_argument('--with-privileged-tests',
                        dest='privileged',
                        default=None,
                        action='store_true')
    # unportable-tests
    parser.add_argument('--with-unportable-tests',
                        dest='unportable',
                        default=None,
                        action='store_true')
    # all-tests
    parser.add_argument('--with-all-tests',
                        dest='alltests',
                        default=None,
                        action='store_true')
    # avoids
    parser.add_argument('--avoid',
                        action='append',
                        dest='avoids',
                        default=None,
                        nargs=1)
    # libtool
    parser.add_argument("--libtool",
                        dest=libtool,
                        default=False,
                        action="store_true")
    # libname
    parser.add_argument('--lib',
                        dest='libname',
                        default=None,
                        nargs=1)
    # sourcebase
    parser.add_argument('--source-base',
                        dest='sourcebase',
                        default=None,
                        nargs=1)
    # m4base
    parser.add_argument('--m4-base',
                        dest='m4base',
                        default=None,
                        nargs=1)
    # pobase
    parser.add_argument('--po-base',
                        dest='pobase',
                        default=None,
                        nargs=1)
    # docbase
    parser.add_argument('--doc-base',
                        dest='docbase',
                        default=None,
                        nargs=1)
    # testsbase
    parser.add_argument('--tests-base',
                        dest='testsbase',
                        default=None,
                        nargs=1)
    # auxdir
    parser.add_argument('--aux-dir',
                        dest='auxdir',
                        default=None,
                        nargs=1)
    # lgpl
    parser.add_argument('--lgpl',
                        dest='lgpl',
                        default=False,
                        type=int,
                        nargs='?')
    # makefile
    parser.add_argument("--makefile-name",
                        dest="makefile",
                        default=None,
                        type=str)
    # symlink
    parser.add_argument('-s', '--symbolic', '--symlink',
                        dest='symlink',
                        default=None,
                        action='store_true')
    # local-symlink
    parser.add_argument('--local-symlink',
                        dest='lsymlink',
                        default=None,
                        action='store_true')
    # All other arguments are collected.
    parser.add_argument("non_option_arguments",
                        nargs='*')

    # Parse the given arguments. Don't signal an error if non-option arguments
    # occur between or after options.
    (cmdargs, unhandled) = parser.parse_known_args()

    # Handle --help and --version, ignoring all other options.
    if cmdargs.help != None:
        print(info.usage())
        sys.exit(0)
    if cmdargs.version != None:
        message = '''gnulib-tool (%s %s)%s\n%s\n%s\n\nWritten by %s.''' % \
            (info.package(), info.date(), info.version(), info.copyright(),
             info.license(), info.authors())
        print(message)
        sys.exit(0)

    # Report unhandled arguments.
    for arg in unhandled:
        if arg.startswith('-'):
            message = '%s: Unrecognized option \'%s\'.\n' % (constants.APP['name'], arg)
            message += 'Try \'gnulib-tool --help\' for more information.\n'
            sys.stderr.write(message)
            sys.exit(1)
    # By now, all unhandled arguments were non-options.
    cmdargs.non_option_arguments += unhandled

    # Determine when user tries to combine modes.
    args = [
        cmdargs.mode_list,
        cmdargs.mode_import,
        cmdargs.mode_add_import,
        cmdargs.mode_remove_import,
        cmdargs.mode_update,
        cmdargs.mode_create_testdir,
        cmdargs.mode_create_megatestdir,
        cmdargs.mode_test,
        cmdargs.mode_megatest,
        cmdargs.mode_xdescription,
        cmdargs.mode_xcomment,
        cmdargs.mode_xstatus,
        cmdargs.mode_xnotice,
        cmdargs.mode_xapplicability,
        cmdargs.mode_xfilelist,
        cmdargs.mode_xdependencies,
        cmdargs.mode_xautoconf,
        cmdargs.mode_xautomake,
        cmdargs.mode_xinclude,
        cmdargs.mode_xlink,
        cmdargs.mode_xlicense,
        cmdargs.mode_xmaintainer,
        cmdargs.mode_copy_file,
    ]
    overflow = [arg for arg in args if arg != None]
    if len(overflow) > 1:
        message = '%s: Unable to combine different modes of work.\n' % constants.APP['name']
        message += 'Try \'gnulib-tool --help\' for more information.\n'
        sys.stderr.write(message)
        sys.exit(1)

    # Determine selected mode.
    if cmdargs.mode_list != None:
        mode = 'list'
    if cmdargs.mode_import != None:
        mode = 'import'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_add_import != None:
        mode = 'add-import'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_remove_import != None:
        mode = 'remove-import'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_update != None:
        mode = 'update'
        if len(cmdargs.non_option_arguments) > 0:
            message = '%s: too many arguments in \'update\' mode\n'
            message += 'Try \'gnulib-tool --help\' for more information.\n'
            message += 'If you really want to modify the gnulib configuration of your project,\n'
            message += 'you need to use \'gnulib-tool --import\' - at your own risk!\n'
            sys.stderr.write(message)
            sys.exit(1)
    if cmdargs.mode_create_testdir != None:
        mode = 'create-testdir'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_create_megatestdir != None:
        mode = 'create-megatestdir'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_test != None:
        mode = 'test'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_megatest != None:
        mode = 'megatest'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_xdescription != None:
        mode = 'extract-description'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_xcomment != None:
        mode = 'extract-comment'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_xstatus != None:
        mode = 'extract-status'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_xnotice != None:
        mode = 'extract-notice'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_xapplicability != None:
        mode = 'extract-applicability'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_xfilelist != None:
        mode = 'extract-filelist'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_xautoconf != None:
        mode = 'extract-autoconf-snippet'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_xautomake != None:
        mode = 'extract-automake-snippet'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_xdependencies != None:
        mode = 'extract-dependencies'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_xinclude != None:
        mode = 'extract-include-directive'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_xlink != None:
        mode = 'extract-link-directive'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_xlicense != None:
        mode = 'extract-license'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_xmaintainer != None:
        mode = 'extract-maintainer'
        modules = list(cmdargs.non_option_arguments)
    if cmdargs.mode_copy_file != None:
        mode = 'copy-file'
        if len(cmdargs.non_option_arguments) < 1 or len(cmdargs.non_option_arguments) > 2:
            message = '%s: *** ' % constants.APP['name']
            message += 'invalid number of arguments for --%s' % mode
            message += '\n%s: *** Stop.\n' % constants.APP['name']
            sys.stderr.write(message)
            sys.exit(1)
        files = list(cmdargs.non_option_arguments)

    # Determine specific settings.
    destdir = cmdargs.destdir
    if destdir != None:
        destdir = cmdargs.destdir[0]
    localpath = cmdargs.localpath
    if localpath != None:
        localpath = [ dir
                      for list1 in localpath
                      for dir in list1 ]
    libname = cmdargs.libname
    if libname != None:
        libname = cmdargs.libname[0]
    auxdir = cmdargs.auxdir
    if auxdir != None:
        auxdir = cmdargs.auxdir[0]
    sourcebase = cmdargs.sourcebase
    if sourcebase != None:
        sourcebase = cmdargs.sourcebase[0]
    m4base = cmdargs.m4base
    if m4base != None:
        m4base = cmdargs.m4base[0]
    pobase = cmdargs.pobase
    if pobase != None:
        pobase = cmdargs.pobase[0]
    testsbase = cmdargs.testsbase
    if testsbase != None:
        testsbase = cmdargs.testsbase[0]
    dryrun = cmdargs.dryrun
    verbose = -cmdargs.quiet + cmdargs.verbose
    inctests = cmdargs.inctests
    flags = [cmdargs.inctests, cmdargs.obsolete, cmdargs.cxx,
             cmdargs.longrunning, cmdargs.privileged, cmdargs.unportable,
             cmdargs.alltests]
    testflags = list()
    for flag in flags:
        index = flags.index(flag)
        if flag != None:
            if flag:
                if index == 0:
                    testflags += [constants.TESTS['tests']]
                elif index == 1:
                    testflags += [constants.TESTS['obsolete']]
                elif index == 2:
                    testflags += [constants.TESTS['cxx-tests']]
                elif index == 3:
                    testflags += [constants.TESTS['longrunning-tests']]
                elif index == 4:
                    testflags += [constants.TESTS['privileged-tests']]
                elif index == 5:
                    testflags += [constants.TESTS['unportable-tests']]
                elif index == 6:
                    testflags += [constants.TESTS['all-tests']]
    lgpl = cmdargs.lgpl
    libtool = cmdargs.libtool
    makefile = cmdargs.makefile
    if lgpl == None:
        lgpl = True
    avoids = cmdargs.avoids
    if avoids != None:
        avoids = [ module
                   for list1 in avoids
                   for module in list1 ]
    symlink = cmdargs.symlink == True
    lsymlink = cmdargs.lsymlink == True

    # Create pygnulib configuration.
    config = classes.GLConfig(
        destdir=destdir,
        localpath=localpath,
        m4base=m4base,
        auxdir=auxdir,
        modules=modules,
        avoids=avoids,
        sourcebase=sourcebase,
        pobase=pobase,
        docbase=docbase,
        testsbase=testsbase,
        testflags=testflags,
        libname=libname,
        lgpl=lgpl,
        makefile=makefile,
        libtool=libtool,
        conddeps=conddeps,
        macro_prefix=macro_prefix,
        podomain=podomain,
        witness_c_macro=witness_c_macro,
        vc_files=vc_files,
        symbolic=symlink,
        lsymbolic=lsymlink,
        modcache=modcache,
        verbose=verbose,
        dryrun=dryrun,
    )

    # Canonicalize the inctests variable.
    if inctests == None:
        if mode in ['import', 'add-import', 'remove-import', 'update']:
            config.disableTestFlag(TESTS['tests'])
        elif mode in ['create-testdir', 'create-megatestdir', 'test', 'megatest']:
            config.enableTestFlag(TESTS['tests'])

    # Work in the given mode.
    if mode in ['list']:
        modulesystem = classes.GLModuleSystem(config)
        listing = modulesystem.list()
        result = '\n'.join(listing)
        os.rmdir(config['tempdir'])
        print(result)

    elif mode in ['import', 'add-import', 'remove-import', 'update']:
        mode = MODES[mode]
        if not destdir:
            destdir = '.'
        config.setDestDir(destdir)

        if mode == MODES['import']:
            # Set variables to default values.
            if not sourcebase:
                sourcebase = 'lib'
            if not m4base:
                m4base = 'm4'
            if not docbase:
                docbase = 'doc'
            if not testsbase:
                testsbase = 'tests'
            if not macro_prefix:
                macro_prefix = 'gl'
            config.setSourceBase(sourcebase)
            config.setM4Base(m4base)
            config.setDocBase(docbase)
            config.setTestsBase(testsbase)
            config.setMacroPrefix(macro_prefix)

            # Perform GLImport actions.
            importer = classes.GLImport(config, mode)
            filetable, transformers = importer.prepare()
            importer.execute(filetable, transformers)

        else:  # if mode != MODE['--import']
            if m4base:
                if not isfile(joinpath(destdir, m4base, 'gnulib-cache.m4')):
                    if not sourcebase:
                        sourcebase = 'lib'
                    if not docbase:
                        docbase = 'doc'
                    if not testsbase:
                        testsbase = 'tests'
                    if not macro_prefix:
                        macro_prefix = 'gl'
                    config.setSourceBase(sourcebase)
                    config.setM4Base(m4base)
                    config.setDocBase(docbase)
                    config.setTestsBase(testsbase)
                    config.setMacroPrefix(macro_prefix)
                # Perform GLImport actions.
                importer = classes.GLImport(config, mode)
                filetable, transformers = importer.prepare()
                importer.execute(filetable, transformers)
            else:  # if not m4base
                m4dirs = list()
                dirisnext = bool()
                filepath = joinpath(destdir, 'Makefile.am')
                if isfile(filepath):
                    with codecs.open(filepath, 'rb', 'UTF-8') as file:
                        data = file.read()
                        data = data.split('ACLOCAL_AMFLAGS')[1]
                        data = data[data.find('=') + 1:data.find('\n')]
                    aclocal_amflags = data.split()
                    for aclocal_amflag in aclocal_amflags:
                        if dirisnext:
                            if not isabs(aclocal_amflag):
                                m4dirs += [aclocal_amflag]
                        else:  # if not dirisnext
                            if aclocal_amflag == '-I':
                                dirisnext = True
                            else:  # if aclocal_amflag != '-I'
                                dirisnext = False
                else:  # if not isfile(filepath)
                    filepath = joinpath(destdir, 'aclocal.m4')
                    if isfile(filepath):
                        pattern = constants.compiler(
                            r'm4_include\(\[(.*?)\]\)')
                        with codecs.open(filepath, 'rb', 'UTF-8') as file:
                            m4dirs = pattern.findall(file.read())
                        m4dirs = [os.path.dirname(m4dir) for m4dir in m4dirs]
                        m4dirs = \
                            [  # Begin filtering
                                m4dir for m4dir in m4dirs \
                                if isfile(joinpath(destdir, m4dir, 'gnulib-cache.m4'))
                            ]  # Finish filtering
                        m4dirs = sorted(set(m4dirs))
                if len(m4dirs) == 0:
                    # First use of gnulib in a package.
                    # Any number of additional modules can be given.
                    if not sourcebase:
                        sourcebase = 'lib'
                    m4base = 'm4'
                    if not docbase:
                        docbase = 'doc'
                    if not testsbase:
                        testsbase = 'tests'
                    if not macro_prefix:
                        macro_prefix = 'gl'
                    config.setSourceBase(sourcebase)
                    config.setM4Base(m4base)
                    config.setDocBase(docbase)
                    config.setTestsBase(testsbase)
                    config.setMacroPrefix(macro_prefix)
                    # Perform GLImport actions.
                    importer = classes.GLImport(config, mode)
                    filetable, transformers = importer.prepare()
                    importer.execute(filetable, transformers)
                elif len(m4dirs) == 1:
                    m4base = m4dirs[-1]
                    config.setM4Base(m4base)
                    # Perform GLImport actions.
                    importer = classes.GLImport(config, mode)
                    filetable, transformers = importer.prepare()
                    importer.execute(filetable, transformers)
                else:  # if len(m4dirs) > 1
                    for m4base in m4dirs:
                        config.setM4Base(m4base)
                        # Perform GLImport actions.
                        importer = classes.GLImport(config, mode)
                        filetable, transformers = importer.prepare()
                        importer.execute(filetable, transformers)

    elif mode == 'create-testdir':
        if not destdir:
            message = '%s: *** ' % constants.APP['name']
            message += 'please specify --dir option'
            message += '\n%s: *** Stop.\n' % constants.APP['name']
            sys.stderr.write(message)
            sys.exit(1)
        if not auxdir:
            auxdir = 'build-aux'
        config.setAuxDir(auxdir)
        testdir = classes.GLTestDir(config, destdir)
        testdir.execute()

    elif mode == 'create-megatestdir':
        if not destdir:
            message = '%s: *** ' % constants.APP['name']
            message += 'please specify --dir option'
            message += '\n%s: *** Stop.\n' % constants.APP['name']
            sys.stderr.write(message)
            sys.exit(1)
        if not auxdir:
            auxdir = 'build-aux'
        config.setAuxDir(auxdir)
        testdir = classes.GLMegaTestDir(config, destdir)
        testdir.execute()

    elif mode == 'test':
        if not destdir:
            destdir = 'testdir%04d' % random.randrange(0, 9999)
        if not auxdir:
            auxdir = 'build-aux'
        config.setAuxDir(auxdir)
        testdir = classes.GLTestDir(config, destdir)
        testdir.execute()
        os.chdir(destdir)
        os.mkdir('build')
        os.chdir('build')
        try:  # Try to execute commands
            sp.call(['../configure'])
            sp.call([UTILS['make']])
            sp.call([UTILS['make'], 'check'])
            sp.call([UTILS['make'], 'distclean'])
        except Exception as error:
            sys.exit(1)
        args = ['find', '.', '-type', 'f', '-print']
        remaining = sp.check_output(args).decode(ENCS['shell'])
        lines = [line.strip()
                 for line in remaining.split('\n') if line.strip()]
        remaining = ' '.join(lines)
        if remaining:
            message = 'Remaining files: %s\n' % remaining
            message += 'gnulib-tool: *** Stop.\n'
            sys.stderr.write(message)
            sys.exit(1)
        os.chdir('../..')
        sp.call(['rm', '-rf', destdir], shell=False)

    elif mode == 'megatest':
        if not destdir:
            destdir = 'testdir %04d' % random.randrange(0, 9999)
        if not auxdir:
            auxdir = 'build-aux'
        config.setAuxDir(auxdir)
        testdir = classes.GLMegaTestDir(config, destdir)
        testdir.execute()
        os.chdir(destdir)
        os.mkdir('build')
        os.chdir('build')
        sp.call(['../configure'])
        sp.call([UTILS['make']])
        sp.call([UTILS['make'], 'check'])
        sp.call([UTILS['make'], 'distclean'])
        args = ['find', '.', '-type', 'f', '-print']
        remaining = sp.check_output(args).decode(ENCS['shell'])
        lines = [line.strip()
                 for line in remaining.split('\n') if line.strip()]
        remaining = ' '.join(lines)
        if remaining:
            message = 'Remaining files: %s\n' % remaining
            message += 'gnulib-tool: *** Stop.\n'
            sys.stderr.write(message)
            sys.exit(1)
        os.chdir('../..')
        sp.call(['rm', '-rf', destdir], shell=False)

    elif mode == 'extract-description':
        modulesystem = classes.GLModuleSystem(config)
        modules = [modulesystem.find(module) for module in modules]
        for module in modules:
            print(module.getDescription())

    elif mode == 'extract-comment':
        modulesystem = classes.GLModuleSystem(config)
        modules = [modulesystem.find(module) for module in modules]
        for module in modules:
            print(module.getComment())

    elif mode == 'extract-status':
        modulesystem = classes.GLModuleSystem(config)
        modules = [modulesystem.find(module) for module in modules]
        for module in modules:
            status = module.getStatus()
            print('\n'.join(status))

    elif mode == 'extract-notice':
        modulesystem = classes.GLModuleSystem(config)
        modules = [modulesystem.find(module) for module in modules]
        for module in modules:
            print(module.getNotice())

    elif mode == 'extract-applicability':
        modulesystem = classes.GLModuleSystem(config)
        modules = [modulesystem.find(module) for module in modules]
        for module in modules:
            print(module.getApplicability())

    elif mode == 'extract-filelist':
        modulesystem = classes.GLModuleSystem(config)
        modules = [modulesystem.find(module) for module in modules]
        for module in modules:
            files = module.getFiles()
            print('\n'.join(files))

    elif mode == 'extract-dependencies':
        result = ''
        if avoids:
            message = '%s: *** ' % constants.APP['name']
            message += 'cannot combine --avoid and --extract-dependencies\n'
            message += '%s: *** Stop.\n' % constants.APP['name']
            sys.stderr.write(message)
            sys.exit(1)
        modulesystem = classes.GLModuleSystem(config)
        modules = [modulesystem.find(module) for module in modules]
        for module in modules:
            dependencies = module.getDependencies()
            if dependencies:
                for depmodule, condition in dependencies:
                    if condition == None:
                        result += '%s\n' % str(depmodule)
                    else:  # if condition != None
                        result += '%s\t%s' % (str(depmodule), condition)
        print(result)

    elif mode == 'extract-autoconf-snippet':
        modulesystem = classes.GLModuleSystem(config)
        modules = [modulesystem.find(module) for module in modules]
        for module in modules:
            print(module.getAutoconfSnippet())

    elif mode == 'extract-automake-snippet':
        modulesystem = classes.GLModuleSystem(config)
        modules = [modulesystem.find(module) for module in modules]
        for module in modules:
            print(module.getAutomakeSnippet())

    elif mode == 'extract-include-directive':
        modulesystem = classes.GLModuleSystem(config)
        modules = [modulesystem.find(module) for module in modules]
        for module in modules:
            print(module.getInclude())

    elif mode == 'extract-link-directive':
        modulesystem = classes.GLModuleSystem(config)
        modules = [modulesystem.find(module) for module in modules]
        for module in modules:
            print(module.getLink())

    elif mode == 'extract-license':
        modulesystem = classes.GLModuleSystem(config)
        modules = [modulesystem.find(module) for module in modules]
        for module in modules:
            print(module.getLicense())

    elif mode == 'extract-maintainer':
        modulesystem = classes.GLModuleSystem(config)
        modules = [modulesystem.find(module) for module in modules]
        for module in modules:
            print(module.getMaintainer())

    elif mode == 'extract-tests-module':
        modulesystem = classes.GLModuleSystem(config)
        modules = [modulesystem.find(module) for module in modules]
        for module in modules:
            if module.getTestsModule():
                print(module.getTestsName())

    elif mode == 'copy-file':
        srcpath = files[0]
        # The second argument is the destination; either a directory ot a file.
        # It defaults to the current directory.
        if len(files) == 2:
            dest = files[1]
        else:  # if len(files) < 2
            dest = '.'
        if not auxdir:
            auxdir = 'build-aux'
        if not sourcebase:
            sourcebase = 'lib'
        if not m4base:
            m4base = 'm4'
        if not docbase:
            docbase = 'doc'
        if not testsbase:
            testsbase = 'tests'
        config.setAuxDir(auxdir)
        config.setSourceBase(sourcebase)
        config.setM4Base(m4base)
        config.setDocBase(docbase)
        config.setTestsBase(testsbase)
        filesystem = classes.GLFileSystem(config)
        lookedup, flag = filesystem.lookup(srcpath)
        if isdir(dest):
            destdir = dest
            if srcpath.startswith('build-aux/'):
                destpath = constants.substart('build-aux/', '%s/' % auxdir, srcpath)
            elif srcpath.startswith('doc/'):
                destpath = constants.substart('doc/', '%s/' % docbase, srcpath)
            elif srcpath.startswith('lib/'):
                destpath = constants.substart('lib/', '%s/' % sourcebase, srcpath)
            elif srcpath.startswith('m4/'):
                destpath = constants.substart('m4/', '%s/' % m4base, srcpath)
            elif srcpath.startswith('tests/'):
                destpath = constants.substart('tests/', '%s/' % testsbase, srcpath)
            elif srcpath.startswith('top/'):
                destpath = constants.substart('top/', '', srcpath)
            else:  # either case
                destpath = srcpath
        else:  # if not isdir(dest)
            destdir = os.path.dirname(dest)
            destpath = os.path.basename(dest)
        # Create the directory for destfile.
        dirname = os.path.dirname(joinpath(destdir, destpath))
        if not config['dryrun']:
            if dirname and not isdir(dirname):
                try:  # Try to create directories
                    os.makedirs(dirname)
                except FileExistsError:
                    pass
        # Copy the file.
        assistant = classes.GLFileAssistant(config)
        tmpfile = assistant.tmpfilename(destpath)
        shutil.copy(lookedup, tmpfile)
        assistant.setOriginal(srcpath)
        assistant.config.setDestDir(destdir)
        assistant.setRewritten(destpath)
        if isfile(joinpath(destdir, destpath)):
            # The file already exists.
            assistant.update(lookedup, flag, tmpfile, True)
        else:  # if not isfile(joinpath(destdir, destpath))
            # Install the file.
            # Don't protest if the file should be there but isn't: it happens
            # frequently that developers don't put autogenerated files under
            # version control.
            assistant.add(lookedup, flag, tmpfile)
        if isfile(tmpfile):
            os.remove(tmpfile)

    else:
        message = '%s: *** ' % constants.APP['name']
        message += 'no mode specified'
        message += '\n%s: *** Stop.\n' % constants.APP['name']
        sys.stderr.write(message)
        sys.exit(1)


if __name__ == '__main__':
    try:  # Try to execute
        main()
    except classes.GLError as error:
        errmode = 0  # gnulib-style errors
        errno = error.errno
        errinfo = error.errinfo
        if errmode == 0:
            message = '%s: *** ' % constants.APP['name']
            if errinfo == None:
                errinfo = ''
            if errno == 1:
                message += 'file %s not found' % errinfo
            elif errno == 2:
                message += 'patch file %s didn\'t apply cleanly' % errinfo
            elif errno == 3:
                message += 'cannot find %s - make sure you run gnulib-tool from within your package\'s directory' % errinfo
            elif errno == 4:
                message += 'minimum supported autoconf version is 2.59. Try adding'
                message += 'AC_PREREQ([%s])' % constants.DEFAULT_AUTOCONF_MINVERSION
                message += ' to your configure.ac.'
            elif errno == 5:
                message += '%s is expected to contain gl_M4_BASE([%s])' % (repr(os.path.join(errinfo, 'gnulib-comp.m4')), repr(errinfo))
            elif errno == 6:
                message += 'missing --source-base option'
            elif errno == 7:
                message += 'missing --doc-base option. --doc-base has been introduced '
                message += 'on 2006-07-11; if your last invocation of \'gnulib-tool '
                message += '--import\' is before that date, you need to run'
                message += '\'gnulib-tool --import\' once, with a --doc-base option.'
            elif errno == 8:
                message += 'missing --tests-base option'
            elif errno == 9:
                message += 'missing --lib option'
            elif errno == 10:
                message = 'gnulib-tool: option --conditional-dependencies is not supported with --with-tests'
            elif errno == 11:
                incompatibilities = ''
                message += 'incompatible license on modules:%s' % constants.NL
                for pair in errinfo:
                    incompatibilities += pair[0]
                    incompatibilities += ' %s' % pair[1]
                    incompatibilities += constants.NL
                tempname = mktemp()
                with codecs.open(tempname, 'wb', 'UTF-8') as file:
                    file.write(incompatibilities)
                sed_table = 's,^\\([^ ]*\\) ,\\1' + ' ' * 51 + ',\n'
                sed_table += 's,^\\(' + '.' * 49 + '[^ ]*\\) *,' + ' ' * 17 + '\\1 ,'
                args = ['sed', '-e', sed_table, tempname]
                incompatibilities = sp.check_output(args).decode(ENCS['default'])
                message += incompatibilities
                os.remove(tempname)
            elif errno == 12:
                message += 'refusing to do nothing'
            elif errno == 13:
                message += 'could not create directory %s' % errinfo
            elif errno == 14:
                message += 'could not delete file %s' % errinfo
            elif errno == 15:
                message += 'could not create file %s' % errinfo
            elif errno == 16:
                message += 'could not transform file %s' % errinfo
            elif errno == 17:
                message += 'could not update file %s' % errinfo
            elif errno == 18:
                message += 'module %s lacks a license' % errinfo
            elif errno == 19:
                message += 'could not create destination directory: %s' % errinfo
            message += '\n%s: *** Stop.\n' % constants.APP['name']
            sys.stderr.write(message)
            sys.exit(1)
