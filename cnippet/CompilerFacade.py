# -----------------------------------------------------------------------------
# Copyright (c) 2017 Leandro T. C. Melo (LTCMELO@GMAIL.COM)
#
# All rights reserved. Unauthorized copying of this file, through any
# medium, is strictly prohibited.
#
# This software is provided on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, explicit or implicit. In no event shall the
# author be liable for any claim or damages.
# -----------------------------------------------------------------------------


import subprocess
import sys
from CommandLine import GccCommand
from Diagnostics import DiagnosticReporter, PREPROCESSING_FILE_FAILED
from Process import execute


class CompilerFacade:
    """ Facade to the host C compiler """

    _id = 'cc'

    GCC = 'GCC'
    Clang = 'Clang'

    def __init__(self, cnip_opt):
        self.host_cc = cnip_opt['host_cc']
        self.host_cc_cmd = cnip_opt["host_cc_cmd"]
        self.host_cc_family = None

    @staticmethod
    def predefined_macros(prefix):
        """
        Defined common builtin/platform macros.
        """

        macros = [
            # Calling conventions
            prefix, '__cdecl=',
            prefix, '__stdcall=',
            prefix, '__thiscall=',

            # Nullability attributes
            prefix, '_Nullable=',
            prefix, '_Nonnull=',

            # GNU alternate keywords
            prefix, '__extension__=',

            # Microsoft
            prefix, "'__declspec(a)='"
        ]

        return macros

    @staticmethod
    def undefined_macros(prefix):
        """
        Undefine common builtin/platform macros.
        """

        macros = [
            # Clang' block language.
            prefix, '__BLOCKS__',
        ]

        return macros

    def verify_support(self):
        """
        Verify whether the host C compiler is supported.
        """

        # Look at predefined macros: $ echo | gcc -dM -E -
        echo = subprocess.Popen('echo', stdout=subprocess.PIPE)
        cmd = [self.host_cc, '-dM', '-E', '-']
        try:
            macros = subprocess.check_output(cmd, stdin=echo.stdout)
        except:
            return False

        #  __GNU__ is predefined in GCC/Clang; __clang__, only in Clang.
        if b'__clang__' in macros:
            self.host_cc_family = CompilerFacade.Clang
        elif b'__GNUC__' in macros:
            self.host_cc_family = CompilerFacade.GCC

        return self.host_cc_family

    def parse_command(self):
        """
        Parse the compiler command to extract compilation options.
        """

        assert self.host_cc_family

        return GccCommand(self.host_cc_cmd)
        # return {
        #           CompilerFacade.GCC: GccCommand(self.host_cc_cmd),
        #           CompilerFacade.Clang: GccCommand(self.host_cc_cmd)
        #       }[self.host_cc_family]

    def check_syntax(self, c_file_name):
        """
        Check the "syntax" of the file -- this is an abuse of terminology, since
        `fsyntax-only' performs symbol lookup, i.e., if a declaration is missing,
        an error is thrown.
        """

        cmd = [self.host_cc,
               '-fsyntax-only',
               c_file_name]

        extra = {
            CompilerFacade.GCC: '-Werror=builtin-declaration-mismatch',
            CompilerFacade.Clang: '-Werror=incompatible-library-redeclaration'
        }

        cmd.append(extra[self.host_cc_family])
        cmd.append('-Werror=incompatible-pointer-types')
        cmd.append('-Werror=implicit-function-declaration')

        return execute(CompilerFacade._id, cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def preprocess(self, c_file_name, pp_file_name):
        """
        Preprocess the file.
        """

        cmd = [self.host_cc,
               '-E',
               '-x',
               'c',
               c_file_name,
               '-o',
               pp_file_name]

        cmd += CompilerFacade.predefined_macros('-D')
        cmd += CompilerFacade.undefined_macros('-U')

        ok = execute(CompilerFacade._id, cmd)
        if ok != 0:
            sys.exit(
                DiagnosticReporter.fatal(PREPROCESSING_FILE_FAILED,
                                         c_file_name))
