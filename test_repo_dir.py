import unittest
import sys
import os
from random_word import RandomWords
from libvcs import repo_create
from libvcs import repo_dir
from libvcs import vcsRepository
import configparser

class repo_dir_test(unittest.TestCase):
    def test_repo_dir_1(self):
        r = RandomWords()
        dest = './test/testFiles/repo_dir'
        if not os.path.exists(dest):
            os.makedirs(dest)

        print('TestCase 1')
        print("Case: Path  doesn't exist and single level dir")
        print('--------------\n')
        path = dest+'/'+ r.get_random_word()
        if os.path.exists(path):
            path = dest + '/' + r.get_random_word()
        else:
            os.makedirs(path)
        dirname = r.get_random_word()
        repo = repo_create(path)
        # calling the function to be tested
        repo_dir(repo, dirname, mkdir=True)
        content = os.listdir(repo.vcsdir)
        # assert for checking if dir is created
        self.assertIn(dirname, content, msg="directory was not created")
        # deleting test directory
        os.system("rm -rf " + path)

    def test_repo_dir_2(self):
        r = RandomWords()
        dest = './test/testFiles/repo_dir'
        if not os.path.exists(dest):
            os.makedirs(dest)

        print('TestCase 2')
        print("Case: Path exists, path is of a dir and single level dir")
        print('--------------\n')
        path = dest+'/'+ r.get_random_word()
        if os.path.exists(path):
            path = dest + '/' + r.get_random_word()
        else:
            os.makedirs(path)
        dirname = r.get_random_word()
        repo = repo_create(path)
        os.makedirs(os.path.join(repo.vcsdir, dirname))
        # calling the function to be tested
        ret = repo_dir(repo, dirname, mkdir=True)
        # assert for checking if dir is created
        self.assertEqual(ret, os.path.join(repo.vcsdir, dirname))
        # deleting test directory
        os.system("rm -rf " + path)


    def test_repo_dir_3(self):
        r = RandomWords()
        dest = './test/testFiles/repo_dir'
        if not os.path.exists(dest):
            os.makedirs(dest)

        print('TestCase 3')
        print("Case: Path exists, path is of a file")
        print('--------------\n')
        path = dest+'/'+ r.get_random_word()
        if os.path.exists(path):
            path = dest + '/' + r.get_random_word()
        else:
            os.makedirs(path)
        filename = r.get_random_word()
        repo = repo_create(path)
        with open(os.path.join(repo.vcsdir, filename), 'w') as f:
            f.write("Testing repo_dir()")
        # calling the function to be tested
        # assert for checking if exception is raised
        with self.assertRaises(Exception) as ex:
            repo_dir(repo, filename, mkdir=True)
            self.assertEqual(ex.msg, "Not a directory {0}".format(os.path.join(repo.vcsdir, filename)))
        # deleting test directory
        os.system("rm -rf " + path)

    def test_repo_dir_4(self):
        r = RandomWords()
        dest = './test/testFiles/repo_dir'
        if not os.path.exists(dest):
            os.makedirs(dest)

        print('TestCase 4')
        print("Case: Path  doesn't exist and mkdir is false")
        print('--------------\n')
        path = dest+'/'+ r.get_random_word()
        if os.path.exists(path):
            path = dest + '/' + r.get_random_word()
        else:
            os.makedirs(path)
        dirname = r.get_random_word()
        repo = repo_create(path)
        # calling the function to be tested
        ret = repo_dir(repo, dirname, mkdir=False)
        # assert for checking if dir is not created
        self.assertEqual(ret, None)
        # deleting test directory
        os.system("rm -rf " + path)

if __name__ == "__main__":
    unittest.main()