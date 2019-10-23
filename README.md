# Overview

tplate is a Jinja2 based templating tool which is designed to enable the creation of projects templates or "starters".  

To use tplate you simply provide a context file containing values for the placeholders in the project template, the
project template directory itself, and the desired output directory. An example is show below:

```sh
tplate  template/dir  output/dir --context=context.json
```

OR

```sh
tplate  github-url  output/dir --context=context.json
```

If a "--context" file is not provided, the user will be prompted to provide values.

# Installation

```sh
pip install tplate
```

# Project Templates

A project template is simply a directory containing the files and directories that make up the project.  Files
that do not end with ".j2" are simply copied to the output directory.  Files ending with the ".j2" suffix are treated
as Jinja2 templates and rendered into the output directory via Jinja2.  For ".j2" files, the file name in the output 
directory will be the template file name minus the ".j2" suffix.  For example, README.md.j2 would be copied to
README.md in the output directory. See the [Jinja2 template designer documentation](http://jinja.palletsprojects.com/en/2.10.x/templates/) 
for details on the templating language.

The template directory must contain a file named tplate.json or tplate.yaml, which contains all of the variables
that are referenced in the template. The  purpose of this file is to document the variables that are in the
templates and to provide default values. If it exists, the user provided context file will be merged with the
default file provided by the project. Also, note that if a context file is not provided, tplate will generate 
the list of variable to prompt for based on this file.

In order to avoid accidentally overwriting existing files, tplate will not do anything if there are any files in the
output directory.  This can be overridden by passing the --update flag

There are some cases when it is desirable for the output directory structure to be determined by a variable.  Most
notably, java package names. To accomplish this, add a file named `tplate_directives.json.j2` or
`tplate_directives.yaml.j2` to the project template similar to the one shown below. This will look for a
directory named 'src/main/java/com/example' in the output directory and rename it to 'src/main/java/new/package/name'.

```json
[
	['java_package_rename','com.example','{{ user_package_name | replace('.','/') }}']
]
```

The structure of this file is a list.  Each list entry is another list with the first argument being the
name of a directive and the remaining arguments being the arguments to the directive.  Note that in the example
above, {{ user_package_name }} is a Jinja2 variable reference.  It assumes that, at run time, a variable called
"user_package_name" will be provided in the "tplate.json" file.  This file will initially be rendered to the output
directory so that the user supplied information can be incorporated.  tplate will then execute the directives and
remove the file.

The template directory argument may also be a git url.  If this is the case, tplate will issue a "git clone" 
command to copy the repository into a temporary directory.  For this to work, the git client must be installed 
and on the path.  

# Additional Notes

- When copying files into the output directory, tplate will ignore (not copy) files and directories with the
  following names: ".git", "tplate.json", "tplate.yaml", ".DS_Store"

# Release Notes

## v1.2

- The template can now be pulled from github by specifying a github project URL instead of an input directory.
- Now supports renaming more than one java packages (e.g. src/main/java and src/test/java).

## v1.1

- The context file no longer needs to be in the output directory.  It can be specified via a separate argument or
  interactively.
- Updated documentation.
- The support for package renaming is more elegantly integrated via the tplate_directives file 

## v1.0.3

- added the "--update" flag to allow overwriting files in the output directory
