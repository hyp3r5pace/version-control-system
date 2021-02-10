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


def repo_find(path=".", required=True):
    """Method to return path to .vcs directory by looking in current directory or recursively in it's parents"""
    """Required to prevent creation of redundant .vcs directory for a repo if it's parent directory already has a .vcs directory"""

    path = os.path.realpath(path)

    if os.path.isdir(os.path.join(path,".vcs")):
        return vcsRepository(path)
    
    parent = os.path.realpath(os.path.join(path, ".."))

    if parent == path:
        # checking the condition when we reach root "/"
        # "/../" == "/"
        if required:
            raise Exception("No .vcs directory")
        else:
            return None

    # recursive call  
    return repo_find(parent, required)



# version control system object creation, storage and retrieval functions
# version control system is a content based file system
# a vcs object is a file whose path or address is computed from it's content
# vcs objects are of various types such as commmit, file or content, tag etc.

class vcsObject(object):
    repo = None
    
    def __init__(self, repo, data=None):
        self.repo = repo
        
        if data != None:
            self.deserialize(data)
    
    def serialize(self):
        """ This function must be implemented by various subclasses.
        Since, objects are of different types on the basis of the data it is storing, different object types are required
        and thus different function and classes"""
        """Read objects content from self.data, a byte string, and do whatever it takes to convert it to a meaningful representation"""
        raise Exception("Unimplemented!!")

    def deserialize(self, data):
        raise Exception('Unimplemented!!')

# subclass of vcsobject class (inheritance from vcsObject class)
class vcsBlob(vcsObject):
    fmt = b'blob'
     
    def serialize(self):
         return self.blobdata
    
    def deserialize(self, data):
        self.blobdata = data



def object_read(repo, sha):
    """Read object object_id from vcs repository repo. Return a
    vcs object whose exact type depends on the object"""

    path = repo_file(repo, "objects", sha[0:2], sha[2:])

    with open(path, "rb") as f:
        raw = zlib.decompress(f.read())

        # computing the starting position of the whitespace in header of the object file
        x = raw.find(b' ')
        fmt = raw[0:x] # the type of object in byte type

        # read and validate object size
        y = raw.find(b'\x00', x)
        size = int(raw[x:y].decode("ascii"))
        if size != len(raw) - y - 1:
            raise Exception("Malformed object {0}: bad length".format(sha))
        
        # picking proper vcs object class
        if fmt == b'commit' :   c = vcsCommit
        elif fmt == b'tree' :   c = vcsTree
        elif fmt == b'tag'  :   c = vcsTag
        elif fmt == b'blob' :   c = vcsBlob
        else:
            raise Exception("Unknown type %s for object %s".format(fmt.decode("ascii"), sha))

        # return object of the class picked above
        return c(repo, raw[y+1:])


def object_write(obj, actually_write=True):
    """Creates the vcs object of input data and writes it to a file in compressed form if actually_write is True"""
    # Serialize object data
    data = obj.serialize() # get the content in byte string format
    # add header
    result = obj.fmt + b' ' + str(len(data)).encode() + b'\x00' + data
    # compute hash
    sha = hashlib.sha1(result).hexdigest()

    if actually_write:
        path = repo_file(obj.repo, "objects", sha[0:2], sha[2:], mkdir=actually_write)

        with open(path, "wb") as f:
            # compress the data and write
            f.write(zlib.compress(result))
    
    return sha


def object_find(repo, name, fmt=None, follow=True):
    """ A name resolution function: Since a vcs object can be refered through various ways such as full hash, short hash,
    tag etc"""
    # unimplemented now (placeholder function) --> will be implemented later
    return name

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

# subparser for vcs cat-file command and associated arguments
"""command format:  vcs cat-file TYPE OBJECT"""
"""Reads a object from repository and deserializes it to create a object of class which supports TYPE"""

argsp = argsubparsers.add_parser("cat-file", help="Provide content of repository object")
argsp.add_argument("type",
                   metavar='type',
                   choices=["blob", "commit", "tag", "tree"],
                   help="Specify the type")

argsp.add_argument("object",
                   metavar="object",
                   help="The object to display")

def cat_file(repo, obj, fmt=None):
    obj = object_read(repo, object_find(repo, obj, fmt=fmt))
    sys.stdout.buffer.write(obj.serialize())


# subparsers for hash-object command and defining associated arguments
""" command format: vcs hash-object [-w] [-t TYPE] FILE"""
"""Reads a FILE and computes the hash of the content of the FILE.
Also, form the object of the corresponding FILE and serialize and store it in repository"""

argsp = argsubparsers.add_parser("hash-object",
                                 help="Computes object ID and optionally creates a blob from a file")
argsp.add_argument("-t",
                   metavar="type",
                   dest="type",
                   choices=["blob", "commit", "tag", "tree"],
                   default="blob",
                   help="Specify the type of the object needed to form")

argsp.add_argument("-w",
                   dest="write",
                   action="store_true",
                   help="Actually write the object to memory disk, database etc")
argsp.add_argument("path",
                   help="Path to the <FILE>")

def object_hash(fd, fmt, repo=None):
    """ Function to read the content of a open file, create appropiate object
        and write the object to vcs directory and return the hash of the file"""

    data = fd.read()

    # choosing constructor on the basis of the object type found in header
    if fmt == b'commit'     : obj = vcsCommit(repo, data)
    elif fmt == b'tree'     : obj = vcsTree(repo, data)
    elif fmt == b'tag'      : obj = vcsTag(repo, data)
    elif fmt == b'blob'     : obj = vcsBlob(repo, data)
    else:
        raise Exception('Unknown type %s!' % fmt)

    return object_write(obj, repo)


# cmd_* function definitions
def cmd_init(args):
    repo_create(args.path)

def cmd_cat_file(args):
    """Calling function for cat-file command"""
    repo = repo_find()
    cat_file(repo, args.object, fmt=args.type.encode())

def cmd_hash_object(args):
    if args.write:
        repo = vcsRepository(".")
    else:
        repo = None
    
    with open(args.path, "rb") as f:
        sha = object_hash(f, args.type.encode(), repo)
        print(sha)


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

