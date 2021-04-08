import unittest
import uuid
import os
import sys
import zlib
import hashlib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libvcs import object_hash
from libvcs import repo_create
import configparser

class obj_hash_test(unittest.TestCase):
    def test_obj_hash_1(self):
        dest = './test/testFiles/obj_hash'
        if not os.path.exists(dest):
            os.makedirs(dest)

        print('TestCase 1')
        print("Case: A simple file is hashed and stored in .vcs/objects dir")
        print('--------------\n')
        path = dest+'/'+ str(uuid.uuid4())
        if os.path.exists(path):
            path = dest + '/' + str(uuid.uuid4())
        else:
            os.makedirs(path)
        # creating the .vcs dir
        repo = repo_create(path)
        # creating a file
        filename = str(uuid.uuid4())
        tmp_path = path + '/' + filename
        with open(tmp_path, 'w') as f:
            f.write('Hello World!')
        with open(tmp_path, 'r') as f:
            # calling function to be tested
            sha = object_hash(f, b'blob', repo)
        # checking if the object hash file is created or not
        tmp_path = os.path.join(repo.vcsdir, 'objects', sha[:2], sha[2:])
        # assertion to check if sha file exists
        self.assertTrue(os.path.exists(tmp_path))
        content = b'blob' + b' ' + str(len(b'Hello World!')).encode() + b'\x00' + b'Hello World!'
        with open(tmp_path, 'rb') as f:
            fileContent = zlib.decompress(f.read())
        self.assertEqual(fileContent, content)
        # deleting test folder
        os.system('rm -rf ' + path)

    def test_obj_hash_2(self):
        dest = './test/testFiles/obj_hash'
        if not os.path.exists(dest):
            os.makedirs(dest)

        print('TestCase 2')
        print("Case: A simple file is hashed and .vcs dir doesn't exist")
        print('--------------\n')
        path = dest+'/'+ str(uuid.uuid4())
        if os.path.exists(path):
            path = dest + '/' + str(uuid.uuid4())
        else:
            os.makedirs(path)
        # creating a file
        filename = str(uuid.uuid4())
        tmp_path = path + '/' + filename
        with open(tmp_path, 'w') as f:
            f.write('Hello World!')
        with open(tmp_path, 'r') as f:
            # calling function to be tested
            sha = object_hash(f, b'blob')
        content = b'blob' + b' ' + str(len(b'Hello World!')).encode() + b'\x00' + b'Hello World!'
        tmp_sha = hashlib.sha1(content).hexdigest()
        # assertion to check if the sha of the blob object matches
        self.assertEqual(sha, tmp_sha)
        # deleting test folder
        os.system('rm -rf ' + path)

if __name__ == "__main__":
    unittest.main()





