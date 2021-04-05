import unittest
from libvcs import repo_create
from libvcs import repo_find
from libvcs import vcsRepository
import os
from random_word import RandomWords
import configparser

class repo_find_test(unittest.TestCase):
    def test_repo_find_1(self):
        r = RandomWords()
        dest = './test/testFiles/repo_find'
        if not os.path.exists(dest):
            os.makedirs(dest)

        print('TestCase 1')
        print('Case: Empty worktree and path is set at root of directory')
        print('--------------\n')
        path = dest+'/'+ r.get_random_word()
        if os.path.exists(path):
            path = dest + '/' + r.get_random_word()
        else:
            os.makedirs(path)
        # creating the .vcs directory
        repo_create(path)
        # calling functions to be tested
        obj = repo_find(path)
        # assertion to verify output of repo_find()
        # object of same type which is returned by repo_find() in this case
        tmp = vcsRepository(os.path.realpath(path))
        self.assertEqual(obj.worktree, tmp.worktree)
        self.assertEqual(obj.vcsdir, tmp.vcsdir)
        self.assertEqual(obj.conf, tmp.conf)
        # deleting test directory
        os.system('rm -rf ' + path)

    def test_repo_find_2(self):
        r = RandomWords()
        dest = './test/testFiles/repo_find'
        if not os.path.exists(dest):
            os.makedirs(dest)

        print('\nTestCase 2')
        print('Case: Non Empty worktree and path is not set at root of directory')
        print('--------------\n')
        path = dest+'/'+ r.get_random_word()
        if os.path.exists(path):
            path = dest + '/' + r.get_random_word()
        else:
            os.makedirs(path)
        # creating the .vcs directory
        repo_create(path)
        # creating files and aditional subdirs
        # files
        with open(os.path.join(path, 'file1.txt'), 'w') as f:
            f.write('Dummy file for test case 2')
        with open(os.path.join(path, 'file2.txt'), 'w') as f:
            f.write('Hello world!')
        # dirs
        tmp_path = os.path.join(path, 'dir1')
        os.makedirs(tmp_path)
        with open(os.path.join(tmp_path, 'file3.txt'), 'w') as f:
            f.write('Hola!')
        tmp_path = os.path.join(path, 'dir2')
        os.makedirs(tmp_path)
        tmp_path = os.path.join(path, 'dir1', 'dir1_1')
        os.makedirs(tmp_path)
        with open(os.path.join(tmp_path, 'file1_1.txt'), 'w') as f:
            f.write('recursive content')
        # calling functions to be tested
        obj = repo_find(tmp_path)
        # assertion to verify output of repo_find()
        # object of same type which is returned by repo_find() in this case
        tmp = vcsRepository(os.path.realpath(path))
        self.assertEqual(obj.worktree, tmp.worktree)
        self.assertEqual(obj.vcsdir, tmp.vcsdir)
        self.assertEqual(obj.conf, tmp.conf)
        # deleting test directory
        os.system('rm -rf ' + path)

    def test_repo_find_3(self):
        r = RandomWords()
        dest = './test/testFiles/repo_find'
        if not os.path.exists(dest):
            os.makedirs(dest)

        print('\nTestCase 3')
        print("Case: Non Empty worktree, path is not set at root of directory and .vcs directory doesn't exist")
        print('--------------\n')
        path = dest+'/'+ r.get_random_word()
        if os.path.exists(path):
            path = dest + '/' + r.get_random_word()
        else:
            os.makedirs(path)
        # creating files and aditional subdirs
        # files
        with open(os.path.join(path, 'file1.txt'), 'w') as f:
            f.write('Dummy file for test case 2')
        with open(os.path.join(path, 'file2.txt'), 'w') as f:
            f.write('Hello world!')
        # dirs
        tmp_path = os.path.join(path, 'dir1')
        os.makedirs(tmp_path)
        with open(os.path.join(tmp_path, 'file3.txt'), 'w') as f:
            f.write('Hola!')
        tmp_path = os.path.join(path, 'dir2')
        os.makedirs(tmp_path)
        tmp_path = os.path.join(path, 'dir1', 'dir1_1')
        os.makedirs(tmp_path)
        with open(os.path.join(tmp_path, 'file1_1.txt'), 'w') as f:
            f.write('recursive content')
        # calling functions to be tested
        # assertion to verify output of repo_find()
        # since repo_find() raises a exception, it must be have a wrapper around it when called so that the raised exception is
        # passed into the wrapper when the function is executed. "With" wrapper is good. Another option is using lambda
        with self.assertRaises(Exception) as excpt:
            repo_find(tmp_path)
            self.assertEqual(excpt.msg, "No .vcs directory")

        # deleting test directory
        os.system('rm -rf ' + path)

if __name__ == "__main__":
    unittest.main()