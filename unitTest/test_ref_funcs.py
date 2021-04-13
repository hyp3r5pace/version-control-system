import unittest
import uuid
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import hashlib
from libvcs import ref_resolve
from libvcs import ref_list
from libvcs import repo_create

class ref_func_test(unittest.TestCase):
    def test_ref_resolve_1(self):
        dest = './test/testFiles/ref_funcs/ref_resolve'
        if not os.path.exists(dest):
            os.makedirs(dest)

        print('TestCase 1')
        print("Case: One level ref file")
        print('--------------\n')
        path = dest+'/'+ str(uuid.uuid4())
        if os.path.exists(path):
            path = dest + '/' + str(uuid.uuid4())
        else:
            os.makedirs(path)
        # creating a .vcs dir
        repo = repo_create(path)
        # creating a file
        filename = str(uuid.uuid4())
        tmp_path = os.path.join(repo.vcsdir, 'refs', filename)
        sha = hashlib.sha1(b'Hola comostas').hexdigest()
        with open(tmp_path, 'w+') as f:
            f.write(sha + '\n')
        # calling the function to be tested
        ret_sha = ref_resolve(repo, 'refs/' + filename)
        # assertion to check if sha value returned by ref_resolve() is same as what is written in file
        self.assertEqual(ret_sha, sha)
        # deleting the test folder
        os.system('rm -rf ' + path)

    def test_ref_resolve_2(self):
        dest = './test/testFiles/ref_funcs/ref_resolve'
        if not os.path.exists(dest):
            os.makedirs(dest)

        print('TestCase 2')
        print("Case: Multi level recursive ref file")
        print('--------------\n')
        path = dest+'/'+ str(uuid.uuid4())
        if os.path.exists(path):
            path = dest + '/' + str(uuid.uuid4())
        else:
            os.makedirs(path)
        # creating a .vcs dir
        repo = repo_create(path)
        # creating a file
        filename = str(uuid.uuid4())
        tmp_path = os.path.join(repo.vcsdir, filename)
        with open(tmp_path, 'w+') as f:
            tmp_filename = str(uuid.uuid4())
            f.write('ref: refs/' + tmp_filename + '\n')
        dirname = str(uuid.uuid4())
        # creating a directory
        os.makedirs(os.path.join(repo.vcsdir, 'refs', dirname))
        with open(os.path.join(repo.vcsdir, 'refs', tmp_filename), 'w') as f:
            tmp_filename = str(uuid.uuid4())
            f.write('ref: refs/' + dirname + '/' + tmp_filename + '\n')
        with open(os.path.join(repo.vcsdir, 'refs', dirname, tmp_filename), 'w') as f:
            sha = hashlib.sha1(b'hola comostas!').hexdigest()
            f.write(sha + '\n')
        # calling the function to be tested
        ret_sha = ref_resolve(repo, filename)
        # assertion to check if sha value returned by ref_resolve() is same as what is written in file
        self.assertEqual(ret_sha, sha)
        # deleting the test folder
        os.system('rm -rf ' + path)

    def test_ref_resolve_3(self):
        dest = './test/testFiles/ref_funcs/ref_resolve'
        if not os.path.exists(dest):
            os.makedirs(dest)

        print('TestCase 3')
        print("Case: Ref file is missing")
        print('--------------\n')
        path = dest+'/'+ str(uuid.uuid4())
        if os.path.exists(path):
            path = dest + '/' + str(uuid.uuid4())
        else:
            os.makedirs(path)
        # creating a .vcs dir
        repo = repo_create(path)
        # creating a file
        filename = str(uuid.uuid4())
        tmp_path = os.path.join(repo.vcsdir, filename)
        with open(tmp_path, 'w') as f:
            tmp_filename = str(uuid.uuid4())
            f.write('ref: refs/' + tmp_filename + '\n')
        # calling the function to be tested
        # assertion to check if missing file exception was raised
        hashValue = ref_resolve(repo, filename)
        self.assertEqual(hashValue, "")
        # deleting the test folder
        os.system('rm -rf ' + path)

        
if __name__ == "__main__":
    unittest.main()