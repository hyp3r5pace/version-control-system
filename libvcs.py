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
    
    with open(repo_file(repo, "userInfo"), "w") as f:
        config = repo_userInfo_config()
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


def repo_userInfo_config():
    """Defines the config file structure and returns the configparser object for UserInfo file"""
    # config files is of microsoft INI format
    ret = configparser.ConfigParser()
    ret.add_section("info")
    ret.set("info", "name", "")
    ret.set("info", "email", "")
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


# commit, tag content parser functions

def keyValueMessageParser(original, start=0, dct=None):
    """Recursive function which parses a commit or a tag message and extracts key value pairs and messages"""
    if not dct:
        dct = collections.OrderedDict()

    # original is a byte string of the commit or tag message
    spaceIndex = original.find(b' ', start)
    newlineIndex = original.find(b'\n', start)

    # if newline arrives before space, then the line must be a empty line
    # thus, it means remainder of the data is a message
    # the if case handles the situation when a blank line is reached and strings after this will be the message 
    if (spaceIndex < 0 or newlineIndex < spaceIndex):
        assert(newlineIndex == start)
        dct[b''] = original[start+1:]
        return dct

    # handling the case before blank line is reached, thus parsing key value is needed
    key = original[start:spaceIndex]
    end = start
    while True:
        end = original.find(b'\n', end+1)
        if original[end+1] != ord(' '):
            break
    
    value = original[spaceIndex+1:end]
    value.replace(b'\n ', b'\n')

    if key in dct:
        if type(dct[key]) == list:
            dct[key].append(value)
        else:
            dct[key] = [dct[key], value]
    else:
        dct[key] = [value]
    
    # recursive function to extract the next key value pair or message
    return keyValueMessageParser(original, end+1, dct)

def keyValueMessageSerialize(keyValueDict):
    """Function which forms the original commit message from the keyValue dictionary formed by keyvalueParser()"""
    res = b''

    for keys in keyValueDict.keys():
        if (keys == b''):
            continue
        
        val = keyValueDict[keys]
        if type(val) != list:
            val = [val]
        
        # adding the key value pairs and recreating the original format
        for elements in val:
            res += keys + b' ' + elements.replace(b'\n', b'\n ') + b'\n'
        
    # adding the blank line and the message after
    res += b'\n' + keyValueDict[b'']

    return res

# subclass of vcs commit --> represents the commits
class vcsCommit(vcsObject):
    fmt=b'commit'

    def serialize(self, data):
        return keyValueMessageSerialize(self.commitData)
    
    def deserialize(self, data):
        self.commitData = keyValueMessageParser(data)


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
    if obj.fmt == b'commit':
        data = obj.serialize(obj.commitData) # get the content in byte string format
    else:
        data = obj.serialize()
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
    if name == "HEAD":
        return ref_resolve(repo, name)
    else:
        return name


# wrapper class for a single record in the tree
class vcsTreeLeaf(object):
    """Wrapper class to a single record"""
    def __init__(self, mode, path, sha):
        self.mode = mode
        self.path = path
        self.sha = sha

def tree_parse_one(raw, start=0):
    """ Function to parse a single record in the tree object"""
    # finding the space terminator of the mode
    x = raw.find(b' ', start)
    # checking if mode provided is correct or not
    assert(x-start == 5 or x-start == 6)

    # read the mode
    mode = raw[start:x]

    # finding the NULL terminator of the path
    y = raw.find(b'\x00', x)
    # and read the path
    path = raw[x+1:y]

    # Read the SHA and convert to an hex string
    sha = hex(int.from_bytes(raw[y+1:y+21], "big"))
    # removing the "0x" substring from the starting of the hex string
    sha = sha[2:]

    return y+21, vcsTreeLeaf(mode, path, sha)

def parse_tree(raw):
    """ Function to parse the whole tree"""
    pos = 0
    max_len = len(raw)
    res = list()
    while pos < max_len:
        pos, data = tree_parse_one(raw, pos)
        res.append(data)
    
    return res

def tree_serialize(obj):
    """Function to serialize a tree object"""
    res = b''
    for i in obj.items:
        res += i.mode
        res += b' '
        res += i.path
        res += b'\x00'
        sha = int(i.sha, 16)
        res += sha.to_bytes(20, byteorder="big")
    
    return res

# class for vcs tree
class vcsTree(vcsObject):
    """Class for vcs tree"""
    # inherited from vcsObject class
    fmt = b'tree'

    def deserialize(self, data):
        self.items = parse_tree(data)

    def serialize(self):
        return tree_serialize(self)




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
    if (fmt == b'commit'):
        sys.stdout.buffer.write(obj.serialize(obj.commitData))
    else:
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


# subparser for vcs log command
"""command format: vcs log [commit]"""
""" This command print the commit history starting from the commit passed as argument"""
argsp = argsubparsers.add_parser("log",
                                 help="Display history starting from a given commit")
argsp.add_argument("commit",
                   default="HEAD",
                   nargs="?",
                   help="commit to start at.")

def logGraph(repo, sha, seen):
    """ Function to print the log of commits by traversing the graph"""
    # seen is a set which stores all the commits which are already visited, thus preventing any circular loop situation in
    # graph travers al.
    if sha in seen:
        return
    seen.add(sha)

    commit = object_read(repo, sha)
    # assertion to check, if the object desrialized is a commit object
    assert(commit.fmt == b'commit')

    if not b'parent' in commit.commitData.keys():
        # the first commit
        return
    
    parents = commit.commitData[b'parent']

    if type(parents) != list:
        parents = [parents]
    
    for p in parents:
        # as data is kept in objects in byte string format
        p = p.decode('ascii')
        print("c_{0} -> c_{1}".format(sha, p))
        logGraph(repo, p, seen)


# subparser for ls-tree command
"""command format: vcs ls-tree [object]"""
""" This commands pretty prints the tree object provided as argument""" 
argsp = argsubparsers.add_parser("ls-tree", help="Print a tree object")
argsp.add_argument("object", help="The tree object hash value")


# subparser for checkout command
"""command format: vcs checkout [commit] [path]"""
"""This commands checkouts a commit or a tree object represented by the commit into a empty directory"""
argsp = argsubparsers.add_parser("checkout", help="Checkout a commit inside of a empty directory")
argsp.add_argument("commit", help="The commit or tree associated with commit to be checked out")
argsp.add_argument("path", help="The empty directory where the tree will be instantiated")

def tree_checkout(repo, tree, path):
    """Recursively instantiates a tree during checkout into a empty directory"""
    for item in tree.items:
        obj = object_read(repo, item.sha)
        rootPath = os.path.realpath(os.path.join(repo.vcsdir, '../'))
        relativePath = item.path.decode().replace(rootPath, '')
        destRootPath = path
        dest = destRootPath + relativePath.encode()

        if obj.fmt == b'tree':
            os.mkdir(dest)
            # recursively call if the object is tree
            tree_checkout(repo, obj, destRootPath)
        elif obj.fmt == b'blob':
            with open(dest, 'wb') as f:
                f.write(obj.blobdata)

# subparser for commit command
"""command format: vcs commit [message] [-a]"""
"""This command commits the current state of the worktree"""
argsp = argsubparsers.add_parser("commit", help="Commit the current state of the working directory")
argsp.add_argument("message", help="mention the commit message")
argsp.add_argument("-a", action="store_true", help="flag to indicate current user is only author of commit not commiter")

def createTree(path=None, actually_write=True):
    """Creates a tree object of the whole repo"""
    """ Todo 
        1. Add a verbose mode to this object creation (which will be turned on by passing a flag in the commit command argument)
        2. Provide a way to check if any changes were made since last commit in the worktree and if not, print "nothing to commit"
    """ 
    repo = repo_find()
    if (path == None):
        path = repo.worktree
    content = os.listdir(path)
    treeContent = list()
    for files in content:
        dest = os.path.join(path, files)
        if os.path.isfile(dest):
            with open(dest, "rb") as f:
                data = f.read()
            blobObj = vcsBlob(repo, data)
            sha = object_write(blobObj, actually_write)
            mode = str(os.stat(dest).st_mode).encode()
            leafObj = vcsTreeLeaf(mode, dest.encode(), sha)
            treeContent.append(leafObj)
        else:
            # when the given files is a directory
            if files != ".vcs":
                leafObj = createTree(dest)
                treeContent.append(leafObj)
    
    treeObj = vcsTree(repo)
    treeObj.items = treeContent
    sha = object_write(treeObj, actually_write)
    if path == repo.worktree:
        return sha
    else:
        mode = str(os.stat(path).st_mode).encode()
        leafObj = vcsTreeLeaf(mode, path.encode(), sha)
        return leafObj


def getObjectFormat(repo, sha):
    """Returns the object format of the object represented by hash"""
    """NOTE: hash has to be a full sha"""
    path = repo_file(repo, "objects", sha[0:2], sha[2:])
    with open(path, "rb") as f:
        raw = zlib.decompress(f.read())

        # computing the starting position of the whitespace in header of the object file
        x = raw.find(b' ')
        fmt = raw[0:x].decode("ascii") # the type of object in ascii string
    return fmt



# this contact info will be used in forming the commit message

def promptUserInfo():
    """Function to prompt user to set user name and email id if missing"""
    repo = repo_find()
    path = repo_file(repo, "userInfo")
    if not os.path.exists(path):
        raise Exception("{0} doesn't exist".format(path))
    # this exception for the case if a directory of the same name is created in .vcs but file doesn't exist
    if not os.path.isfile(path):
        raise Exception("{0} is not a file".format(path))
    
    f = open(path)
    content = f.read()

    parser = configparser.ConfigParser()
    parser.read_string(content)

    if not parser["info"]["name"]:
        print("User name missing")
        # todo: print the set user config command syntax here
        print("Set user name using command")
        exit()
    
    if not parser["info"]["email"]:
        print("User email missing")
        # todo: print the set user config command syntax here
        print("Set user email using command")
        exit()

def getUserInfo():
    """Function to fetch user name and email id from userInfo config file"""
    repo = repo_find()
    path = repo_file(repo, "userInfo")
    f = open(path)
    content = f.read()
    parser = configparser.ConfigParser()
    parser.read_string(content)
    name = parser["info"]["name"]
    email = parser["info"]["email"]

    return name, email

def ref_resolve(repo, ref):
    """Recursively finds the sha-1 of objects referenced by a ref"""
    if not os.path.isfile(repo_file(repo, ref)):
        open(repo_file(repo, ref), 'w+') # creating a empty file if not exists
    with open(repo_file(repo, ref), 'r') as fp:
        data = fp.read()[:-1] # reject the '\n' at the end of the string 
    if data.startswith("ref: "):
        return ref_resolve(repo, data[5:])
    else:
        return data

def update_master(repo, sha):
    with open(repo_file(repo, 'HEAD'), 'r') as fp:
        data = fp.read()[:-1] # rejects the '\n' at the end of the string
    if data.startswith("ref: "):
        path = data[5:]
    with open(repo_file(repo, path), 'w+') as fp:
        fp.write(sha + '\n')

# subparser for vcs set command
"""command format: vcs set [name] [email]"""
"""Set the values of variables in config files present in vcs"""
argsp = argsubparsers.add_parser("set", help="set values of variables in config files")
argsp.add_argument("--name", default="", help="set the name of the user")
argsp.add_argument("--email", default="", help="set the email id of the user")

# cmd_* function definitions
def cmd_init(args):
    """calling function for init command"""
    repo_create(args.path)

def cmd_cat_file(args):
    """Calling function for cat-file command"""
    repo = repo_find()
    cat_file(repo, args.object, fmt=args.type.encode())

def cmd_hash_object(args):
    """calling function for hash-object command"""
    if args.write:
        repo = vcsRepository(".")
    else:
        repo = None
    
    with open(args.path, "rb") as f:
        sha = object_hash(f, args.type.encode(), repo)
        print(sha)

def cmd_log(args):
    """Calling function for log command"""
    repo = repo_find()
    print("digraph vcslog{")
    logGraph(repo, object_find(repo, args.commit), set())
    print("}")

def cmd_ls_tree(args):
    """ Calling function for ls-tree command"""
    repo = repo_find()
    obj = object_read(repo, object_find(repo, args.object, fmt=b'tree'))

    for item in obj.items:
        print("{0} {1} {2}\t{3}".format(
            "0" * (6 - len(item.mode)) + item.mode.decode("ascii"),
            object_read(repo, item.sha).fmt.decode("ascii"),
            item.sha,
            item.path.decode("ascii")))


def cmd_checkout(args):
    """ Calling function for vcs checkout command"""
    repo = repo_find()
    # deserializing the commit byte data and forming the commit object
    obj = object_read(repo, object_find(repo, args.commit))

    # deserializing the tree byte object mentioned in commit object
    if obj.fmt == b'commit':
        obj = object_read(repo, obj.commitData[b'tree'][0].decode("ascii"))
    
    # verify that the path mentioned in the argument is empty
    if os.path.exists(args.path):
        if not os.path.isdir(args.path):
            raise Exception("{0} is not a directory".format(args.path))
        if os.listdir(args.path):
            raise Exception("Directory is not empty")
    else:
        os.makedirs(args.path)
    
    tree_checkout(repo, obj, os.path.realpath(args.path).encode())


def cmd_commit(args):
    """calling function for vcs commit function"""
    if not args.message:
        raise Exception("Commit message is empty")
    # check if user email and name is present or not
    promptUserInfo()
    repo = repo_find()
    dct = collections.OrderedDict()

    treeHash = createTree().encode()
    headPath = os.path.join(repo.vcsdir, "HEAD")
    if not os.path.exists(headPath):
        raise Exception("{0} doesn't exist".format(headPath))
    if not os.path.isfile(headPath):
        raise Exception("{0} is not a file".format(headPath))

    # HEAD file is expected to have commit hash in ascii string format
    headCommitHash = ref_resolve(repo, 'HEAD')
    # -------------- DEBUG ----------------------
    # print("Head commit hash --> " + headCommitHash)
    # -------------------------------------------
    if headCommitHash:
        # check if the commit hash (sha-1) exists or not
        if not os.path.isfile(os.path.join(repo.vcsdir, "objects", headCommitHash[:2], headCommitHash[2:])):
            raise Exception("Commit pointed by HEAD --> {0} doesn't exist".format(headCommitHash))
        # check if the hash in HEAD is a commit object hash
        fmt = getObjectFormat(repo, headCommitHash)
        if fmt != "commit":
            raise Exception("Object pointed by HEAD --> {0} is not a commit".format(headCommitHash))
    
    name, email = getUserInfo()

    # todo: add optional pgp signature component of commit
    dct[b'tree'] = treeHash
    if headCommitHash:
        # add parent if headCommitHash is not empty,ie, first commit will not have a parent commit entry
        dct[b'parent'] = headCommitHash.encode()
    dct[b'author'] = name.encode() + b' ' + email.encode()
    if not args.a:
        dct[b'committer'] = name.encode() + b' ' + email.encode()
    dct[b''] = args.message.encode()
    commitObj = vcsCommit(repo)
    commitObj.commitData = dct
    sha = object_write(commitObj, True)
    # updating the HEAD commit
    update_master(repo, sha)
    print("commit hash: {0}".format(sha))
    print("commit message: {0}\n".format(args.message)) 


def cmd_set(args):
    """calling function for vcs set function"""
    repo = repo_find()
    path = repo_file(repo, "userInfo")
    f = open(path)
    content = f.read()
    parser = configparser.ConfigParser()
    parser.read_string(content)
    if args.name:
        parser["info"]["name"] = args.name
    if args.email:
        parser["info"]["email"] = args.email
    
    with open(path, "w") as f:
        parser.write(f)



def main(argv = sys.argv[1:]):
    args = argparser.parse_args(argv)

    if args.command == "add"                   : cmd_add(args)
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
    elif args.command == "set"                 : cmd_set(args)