#!/usr/bin/env python3
import sys

import argparse
import datetime
import re
import subprocess
from typing import Tuple

parser = argparse.ArgumentParser(
    description='Tags and releases the next version of this project.',
)

parser.add_argument(
    'tag',
    help='Semantic version number to use as the tag.',
)

parser.add_argument(
    '-e', '--edit',
    action='store_true',
    help="Force edits of git commits.",
)

parser.add_argument(
    '-n', '--dry-run',
    action='store_true',
    help="Don't modify files or push to git.",
)

parser.add_argument(
    '-v', '--verbose',
    action='store_true',
    help='Print debug information.',
)

def parse_changelog(args) -> Tuple[str, str]:
    """Return an updated changelog and and the list of changes.
    """
    with open('CHANGELOG.md', 'r') as file:
        match = re.match(
            pattern=r'(.*?## \[Unreleased]\n)(.+?\n)(\n*## \[.*)',
            string=file.read(),
            flags=re.DOTALL,
        )
    header, changes, tail = match.groups()
    tagged = '\n## [%s] - %s\n%s' % (
        args.tag, datetime.date.today().isoformat(), changes)
    if args.verbose:
        print(tagged)

    return ''.join((header, tagged, tail)), changes


VERSION_SOURCE = """\
{head}
#define TCOD_MAJOR_VERSION  {major}
#define TCOD_MINOR_VERSION  {minor}
#define TCOD_PATCHLEVEL     {patch}

#define TCOD_STRVERSION "{tag}"
{tail}"""

def update_version_header(args):
    """Update version.h to use the given tag."""
    with open('src/libtcod/version.h', 'r') as f:
        match = re.match(
            pattern=r'(?P<head>.*?)\n#define TCOD_MAJOR_VERSION.*?TCOD_STRVERSION[^\n]*\n(?P<tail>.*)',
            string=f.read(),
            flags=re.DOTALL,
        )
    fargs = {'tag': args.tag}
    fargs.update(match.groupdict())

    match = re.match(
        pattern=r'(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)',
        string=args.tag,
    )
    fargs.update(match.groupdict())

    source = VERSION_SOURCE.format(**fargs)

    if not args.dry_run:
        with open('src/libtcod/version.h', 'w') as f:
            f.write(source)

def main():
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    if args.verbose:
        print(args)

    update_version_header(args)
    new_changelog, changes = parse_changelog(args)

    if not args.dry_run:
        with open('CHANGELOG.md', 'w') as f:
            f.write(new_changelog)
        edit = ['-e'] if args.edit else []
        subprocess.check_call(
            ['git', 'commit', '-avm', 'Prepare %s release.' % args.tag] + edit,
        )
        subprocess.check_call(
            ['git', 'tag', args.tag, '-a', '-m',
             '%s\n\n%s' % (args.tag, changes)] + edit,
        )
        subprocess.check_call(
            ['git', 'push', '--follow-tags'],
        )

if __name__ == '__main__':
    main()
