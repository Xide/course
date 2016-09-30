#!/usr/bin/env python3

import sys
import argparse
import os

# rm -r
from shutil import rmtree
from json import load, dump
from pprint import pprint

def create_directory(base, course_id):
    """
    Create course directory at base/course_id
    Bundle a directory removal/recreation if course already exists
    """
    dir_path = os.path.join(base, course_id)
    try:
        os.mkdir(dir_path)
        print('Course base directory created :', dir_path)
    except FileExistsError:
        print('Course %s already exists' % course_id)
        rm = input('Would you like to remove existing folder %s ? [y/N] : ' %
                    os.path.abspath(dir_path))
        if rm.lower() == 'y':
            try:
                rmtree(os.path.abspath(dir_path))
                create_directory(base, course_id)
            except Exception as e:
                print('Error encoutered while removing directory:', e)
                return False
        else:
            return False
    return True

def id_detect(d):
    """
    Auto detect next free id in directory d
    """
    mx = 0
    for f in os.listdir(d):
        if os.path.isdir(os.path.join(d, f)):
            try:
                i = int(f)
                mx = max(mx, i)
            except:
                pass
    print('Detected course ID:', mx + 1)
    return mx + 1

def build_parser():
    """
    CLI parser generator using argparse
    """
    parser = argparse.ArgumentParser(description='Create course folder.')
    parser.add_argument('subject',
                        type=str,
                        help='Course discipline subject')

    parser.add_argument('-id',
                        type=int,
                        help='Course id',
                        default=None)

    parser.add_argument('-t', '--title',
                        dest='course',
                        type=str,
                        help='Course title',
                        default=None)
    parser.add_argument('-c', '--conf',
                        dest='conf',
                        type=str,
                        help='Configuration path file (default: ~/.kentrc)',
                        default=os.path.join(os.path.expanduser('~'), '.kentrc'))

    return parser

def sanitize_args(conf, args):
    """
    Ensure conf and args are filled with the right values
    before entering the program
    """
    args.subject = args.subject.lower().replace(' ', '_')
    if not os.path.exists(conf['base']):
        cr = input('Base directory %s does not exits, create it ? [Y/n] : ' % conf['base'])
        if cr.lower() != 'n':
            os.mkdir(conf['base'])
    try:
        # Ensure subject directory exists
        subject_base = os.path.join(conf['base'], args.subject)
        os.mkdir(subject_base)
        print('Created subject base directory:', subject_base)
    except:
        pass

    if not args.id:
        args.id = id_detect(os.path.join(conf['base'], args.subject))
    return args

def generate_configuration(path):
    """
    Ask informations to the user at first launch or when config
    is missing at "path", and create the file if needed
    """
    conf = {}
    conf['base'] = os.path.abspath(os.path.expanduser(input('Enter base courses directory : ')))
    pprint(conf, indent=2)
    confirm = input('Is this configuration correct ? [Y/n] : ')
    if confirm.lower() == 'n':
        return generate_configuration(path)
    with open(path, 'w') as f:
        dump(conf, f)

def load_conf_file(path):
    try:
        with open(path, 'r') as raw_conf:
            conf = load(raw_conf)
            return conf
    except ValueError as e:
        print('Incorrect config file encoutered :', e)
        return None
    except FileNotFoundError as e:
        print('Missing config file', path)
        cr = input('Would you like to generate one at this path ? [Y/n] : ')
        if cr.lower() != 'n':
            generate_configuration(path)
            return load_conf_file(path)

if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()

    conf = load_conf_file(args.conf)
    if not conf:
        sys.exit(1)

    # Set course_subject before args.subject get sanitized (lower + replace ' ', '_')
    course_subject = args.subject
    args = sanitize_args(conf, args)
    if not args:
        sys.exit(1)

    course_id = '%03d' % args.id
    course_title = args.course
    course_dir_base = os.path.join(conf['base'], args.subject)
    course_dir = os.path.join(course_dir_base, course_id)

    # Course title input
    if not course_title:
        title = input('Course title (default: %s) : ' % course_id).strip()
        if not title:
            course_title = course_id
        else:
            course_title = title

    # Course directory creation
    if not create_directory(course_dir_base, course_id):
        sys.exit(1)


    # Creating markdown file
    print('Creating Markdown course')
    with open(os.path.join(course_dir, '%s.md' % course_title.lower().replace(' ', '_')), 'w') as md:
        md.write("""
# %s

Author

---

## Definitions

Label       | Definition
------------|---------------

""" % course_title)

    print('Creating subfolders')
    os.mkdir(os.path.join(course_dir, 'assets'))
    os.mkdir(os.path.join(course_dir, 'images'))
