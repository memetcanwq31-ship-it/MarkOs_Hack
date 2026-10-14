#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Yerli Veil Framework - github.com/memetcanwq31

import argparse
import sys
from lib.common import helpers, messages, orchestra

sys.dont_write_bytecode = True

if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    parser = argparse.ArgumentParser(
        add_help=False,
        description="Yerli Veil - Turkish native payload framework")

    parser.add_argument('-h', '-?', '--h', '-help', '--help',
                        action="store_true", help=argparse.SUPPRESS)

    veilframework = parser.add_argument_group('[*] Yerli Veil Options')
    veilframework.add_argument('--list-tools', action="store_true", default=False)
    veilframework.add_argument('-t', '--tool', metavar='TOOL', default=False,
                               help='Tool to use (Evasion, Ordnance)')
    veilframework.add_argument('--update', action='store_true')
    veilframework.add_argument('--config', action='store_true')
    veilframework.add_argument('--version', action="store_true")
    veilframework.add_argument('--clean', action='store_true',
                               help='Clean out payload output folders')

    payload_args = parser.add_argument_group('[*] Payload Settings')
    payload_args.add_argument('--list-payloads', action='store_true', default=False)

    evasion_args = parser.add_argument_group('[*] Yerli-Evasion Options')
    evasion_args.add_argument('-p', metavar="PAYLOAD", nargs='?', const="list",
                              help='Payload to generate (e.g. python/aes_xor_rev)')
    evasion_args.add_argument('-o', metavar="OUTPUT-NAME", default="payload")
    evasion_args.add_argument('-c', metavar='OPTION=value', nargs='*', default=None,
                              help='Custom options: LHOST=1.2.3.4 LPORT=4444 KEY=secret')
    evasion_args.add_argument('--compiler', default='pyinstaller')

    ordnance_args = parser.add_argument_group('[*] Yerli-Ordnance Options')
    ordnance_args.add_argument('--ordnance-payload', metavar="PAYLOAD",
                               default='windows/meterpreter/reverse_tcp',
                               help='msfvenom payload type')
    ordnance_args.add_argument('--msfoptions', metavar="OPTION=value", nargs='*',
                               help='msfvenom options: LHOST=x.x.x.x LPORT=4444')
    ordnance_args.add_argument('-e', '--encoder', metavar="ENCODER",
                               default=None, help='Encoder: xor, xor_dynamic, base64')
    ordnance_args.add_argument('-b', '--bad-chars', metavar="\\x00\\x0a..", default=None)
    ordnance_args.add_argument('--print-stats', action='store_true', default=False)

    args = parser.parse_args()
    conductor = orchestra.Conductor(args)

    if args.h:
        parser.print_help()
    elif args.version:
        messages.title_screen()
    elif args.update:
        conductor.update_veil()
    elif args.config:
        conductor.config_veil()
    elif args.list_tools:
        conductor.list_tools()
    elif args.clean:
        helpers.clean_payloads()
    elif not args.tool:
        conductor.main_menu()
    else:
        conductor.command_line_use()
