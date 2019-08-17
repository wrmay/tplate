import argparse
import jinja2
import json
import os.path
import shutil
import sys
import yaml

TPLATE_SUFFIX = '.j2'

# files in this list are allowed in the output directory.
ALLOW_IN_OUTDIR_LIST = ['.DS_Store']
NOCOPY_LIST = ['tplate.yaml', 'tplate.json', '.git', '.DS_Store']


def loadfile(filename):
    result = None
    with open(filename, 'r') as f:
        if filename.endswith('.json'):
            result = json.load(f)
        elif filename.endswith('.yaml') or filename.endswith('.yml'):
            result = yaml.safe_load(f)

    return result


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('template_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--context', )
    parser.add_argument('--update', action='store_true')

    args = parser.parse_args(sys.argv[1:])
    if not os.path.isdir(args.template_dir):
        sys.exit('The program has exited because the provided template directory ({0}) does not exist.'
                 .format(args.template_dir))

    if os.path.isfile(args.output_dir):
        sys.exit('The program has exited because the specified output directory is a file.')

    if os.path.isdir(args.output_dir):
        files = os.listdir(args.output_dir)
        files = [f for f in files if f not in ALLOW_IN_OUTDIR_LIST]
        if (not args.update) and (len(files) > 0):
            sys.exit('The program is exiting because the output directory ({0}) is not empty.'.format(args.output_dir))

    else:
        os.makedirs(args.output_dir)

    context_file = os.path.join(args.template_dir, 'tplate.json')
    if os.path.exists(context_file):
        environment = loadfile(context_file)

    else:
        context_file = os.path.join(args.template_dir, 'tplate.yaml')
        if os.path.exists(context_file):
            environment = loadfile(context_file)

        else:
            sys.exit('The program is exiting because a required file (tplate.json or tplate.yaml) was not found in '
                     'the output directory ({0}).'.format(args.output_dir))

    # if a context file was provided, load it on top of the defaults
    if args.context is not None:
        if not os.path.isfile(args.context):
            sys.exit('The program is exiting because the specified context file ({0}) does not exist.'
                     .format(args.context))

        if (not args.context.endswith('.json')) \
                and (not args.context.endswith('.yaml')) \
                and (not args.context.endswith('.yml')):
            sys.exit('The program is exiting because the context argument ({0}) has an unsupported extension. Context '
                     'files must end with ".json" or ".yaml" or "yml.'.format(args.context))

        uservals = loadfile(args.context)

    # otherwise prompt for input
    else:
        uservals = promptforinput(environment)

    environment.update(uservals)

    # add the output path and template path to the environment
    environment['output_dir'] = args.output_dir
    environment['template_dir'] = args.template_dir

    copydir(args.template_dir, args.output_dir, environment)

    directives = None
    path = os.path.join(args.output_dir, 'tplate_directives.json')
    if os.path.exists(path):
        directives = loadfile(path)
    else:
        path = os.path.join(args.output_dir, 'tplate_directives.yaml')
        if os.path.exists(path):
            directives = loadfile(path)

    if directives is not None:
        do_directives(args, directives)
        os.remove(path)


def do_directives(args, directives):
    for directive in directives:
        if directive[0] == 'java_package_rename':
            frompath = os.path.join(args.output_dir, 'src', 'main', 'java', *(directive[1].split('.')))
            topath = os.path.join(args.output_dir, 'src', 'main', 'java', *(directive[2].split('.')))
            shutil.rmtree(topath,ignore_errors=True)
            os.renames(frompath,topath)
            # print('>>> java_package_rename {0} {1}'.format(frompath, topath))
            # shutil.rmtree(topath, ignore_errors=True)
            # os.makedirs(topath,exist_ok=True)
            # simplecopy(frompath,topath)
            # shutil.rmtree(frompath)
            # remove_empty_dirs(os.path.join(args.output_dir, 'src', 'main', 'java'))
        else:
            # just ignore unknown directives
            pass


def remove_empty_dirs(adir):
    file_list = os.listdir(adir)
    for f in file_list:
        subdir = os.path.join(adir,f)
        if os.path.isdir(subdir):
            remove_empty_dirs(subdir)

    # after removing empty directories
    file_list = os.listdir(adir)
    if len(file_list) == 0:
        os.rmdir(adir)


def promptforinput(userenv):
    done = False
    userinput = dict()
    while not done:
        print('Please provide values for the following template variables:')
        for key in userenv:
            userinput[key] = input('{0} ({1}): '.format(key, userenv[key]))

        print('You have provided the following values:')
        for key, val in userinput.items():
            print('\t{0}={1}'.format(key, val))
        yn = input('Enter y to proceed or n to re-enter values: ')
        if yn.lower() == 'y':
            done = True
        else:
            done = False

    return userinput


# simple copy without templating
def simplecopy(fromdir, todir):
    for f in os.listdir(fromdir):
        infile = os.path.join(fromdir, f)
        if os.path.isdir(infile):
            to = os.path.join(todir, f)
            os.makedirs(to, exist_ok=True)
            simplecopy(infile, to)
        else:
            outfile = os.path.join(todir, f)
            shutil.copyfile(infile, outfile)


# copy with templating
def copydir(fromdir, todir, environment):
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(fromdir), trim_blocks=True, lstrip_blocks=True)
    for f in os.listdir(fromdir):
        if f in NOCOPY_LIST:
            continue

        infile = os.path.join(fromdir, f)
        if os.path.isdir(infile):
            to = os.path.join(todir, f)
            os.makedirs(to, exist_ok=True)
            copydir(infile, to, environment)
        else:
            if f.endswith(TPLATE_SUFFIX):
                template = template_env.get_template(f)
                outfile = os.path.join(todir, f[0:-1 * len(TPLATE_SUFFIX)])
                with open(outfile, 'wt') as fp:
                    template.stream(environment).dump(fp)

            else:
                outfile = os.path.join(todir, f)
                shutil.copyfile(infile, outfile)
