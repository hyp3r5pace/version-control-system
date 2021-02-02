# importing various library
import argparse
import collections
import hashlib
import os
import re
import sys
import zlib
import configparser

# utility functions
def repo_path(repo, *path):
    """Compute path under repo's vcsdir"""
    return os.path.join(repo.vcsdir, *path)


def repo_dir(repo, *path, mkdir=False):
    """creates directories mentioned in *path if absent"""

    path = repo_path(repo, *path)

    if os.path.exists(path):
        if (os.path.isdir(path)):
            return path
        else:
            raise Exception("Not a directory %s" % path)

    if mkdir:
        os.makedirs(path)
        return path
    else:
        return None



def repo_file(repo, *path, mkdir=False):
    """Creates directories to the file mentioned in *path if absent"""

    # checks if path to file exist, if not creates using repo_dir() function.
    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)



# class to define a git repository object
class vcsRepository(object):
    """Abstraction of a vcs repository"""

    worktree = None
    vcsdir = None
    conf = None

    def __init__(self, path, force=False):
        self.worktree = path
        self.vcsdir = os.path.join(path, ".vcs")

        #  Read configuration file in .git/config
        self.conf = configparser.ConfigParser()
        cf = repo_file(self, "config")

        if cf and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:
            raise Exception("Configuration file missing")

        if not force:
            vers = int(self.conf.get("core", "repositoryformatversion"))
            if vers != 0:
                raise Exception("Unsupported repositoryformatversion %s" % vers)
    


def repo_create(path):
    """Create a new repository at path"""

    repo = vcsRepository(path, True) # create a vcs repo object

    # first check if path provided exists or is an empty directory
    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            raise Exception("%s is not a directory" % path)
        if os.listdir(repo.worktree):
            raise Exception("%s is not empty" % path)
    else:
        os.makedirs(repo.worktree)

    assert(repo_dir(repo, "branches", mkdir=True))
    assert(repo_dir(repo, "objects", mkdir=True))
    assert(repo_dir(repo, "refs", "tags", mkdir=True))
    assert(repo_dir(repo, "refs", "heads", mkdir=True))
    

    # .vcs/description
    with open(repo_file(repo, "description"), "w") as f:
        f.write("Unnamed repository; edit this desscription to name the repository\n")
    
    # .vcs/HEAD
    with open(repo_file(repo, "HEAD"), "w") as f:
        f.write("ref: refs/heads/master\n")
    
    # write default content to vcs config file
    with open(repo_file(repo, "config"), "w") as f:
        config = repo_default_config()
        config.write(f)
    
    return repo


def repo_default_config():
    """Defines the config file structure and returns the configparser object"""
    # config files is of microsoft INI format

    ret = configparser.ConfigParser()

    ret.add_section("core")
    ret.set("core", "repositoryformatversion", "0")
    ret.set("core", "filemode", "false")
    ret.set("core", "bare", "false")

    return ret




# command line argument parsing
argparser = argparse.ArgumentParser()
argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True

# agument parser for vcs init terminal command
argsp = argsubparsers.add_parser("init", help="Initialize a new, empty directory")
argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=".",
                   help="where to create the repository")

# cmd_* function definitions
def cmd_init(args):
    repo_create(args.path)


def main(argv = sys.argv[1:]):
    args = argparser.parse_args(argv)

    if args.command == "add"                 : cmd_add(args)
    elif args.command == "cat-file"            : cmd_cat_file(args)
    elif args.command == "checkout"            : cmd_checkout(args)
    elif args.command == "commit"              : cmd_commit(args)
    elif args.command == "hash-object"         : cmd_hash_object(args)
    elif args.command == "log"                 : cmd_log(args)
    elif args.command == "init"                : cmd_init(args)
    elif args.command == "ls-tree"             : cmd_ls_tree(args)
    elif args.command == "merge"               : cmd_merge(args)
    elif args.command == "rebase"              : cmd_rebase(args)
    elif args.command == "rev-parse"           : cmd_rev_parse(args)
    elif args.command == "rm"                  : cmd_rm(args)
    elif args.command == "show-ref"            : cmd_show_ref(args)
    elif args.command == "tag"                 : cmd_tag(args)

