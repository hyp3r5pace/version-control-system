import unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libvcs import repo_create
import configparser
from random_word import RandomWords

class initTest(unittest.TestCase):
    # testcase: empty directory
    def test_init_1(self):
        r = RandomWords()
        dest = './test/testFiles/init'
        if not os.path.exists(dest):
            os.makedirs(dest)

        print('TestCase 1')
        print('Case: Empty Directory')
        print('--------------\n')
        path = dest+'/'+ r.get_random_word()
        if os.path.exists(path):
            path = dest + '/' + r.get_random_word()
        else:
            os.makedirs(path)
        # calling the function to be tested
        repo_create(path)
        files = os.listdir(path)
        # assertion to ensure .vcs directory is created
        self.assertIn('.vcs', files, msg=".vcs is not created")
        tmp_path = os.path.join(path, files[0])
        files = os.listdir(tmp_path)
        # assertion to ensure number of files inside .vcs is 7
        self.assertEqual(len(files), 7)
        # assertion to ensure if HEAD exist in .vcs dir
        self.assertIn('HEAD', files, msg="HEAD is not created")
        # assertion to ensure if 'branches directory is created
        self.assertIn('branches', files, msg="branches dir is not created")
        # assertion to ensure if config file is created
        self.assertIn('config', files, msg="config is not created")
        # assertion to ensure if description file is created
        self.assertIn('description', files, msg="description is not created")
        # assertion to ensure if objects dir is created
        self.assertIn('objects', files, msg="objects dir is not created")
        # assertion to ensure if refs dir is created
        self.assertIn('refs', files, msg="refs dir is not created")
        # assertion to ensure if userInfo file is created
        self.assertIn('userInfo', files, msg="userInfo files is not created")
        # tests for files
        # HEAD file
        tmp = os.path.join(tmp_path, 'HEAD')
        with open(tmp, 'r') as f:
            text = f.read()
        # assertion to check if default content of HEAD file
        self.assertEqual(text, 'ref: refs/heads/master\n')
        # description
        tmp = os.path.join(tmp_path, 'description')
        with open(tmp, 'r') as f:
            text = f.read()
        # assertion to check if default content of description file
        self.assertEqual(text, 'Unnamed repository; edit this desscription to name the repository\n')
        # config
        tmp = os.path.join(tmp_path, 'config')
        with open(tmp, 'r') as f:
            text = f.read()
        parser = configparser.ConfigParser()
        parser.read_string(text)
        # assertion to check default content of config file
        self.assertEqual(len(parser['core']), 3)
        self.assertEqual(parser['core']['repositoryformatversion'], '0')
        self.assertEqual(parser['core']['filemode'], 'false')
        self.assertEqual(parser['core']['bare'], 'false')
        # userInfo
        tmp = os.path.join(tmp_path, 'userInfo')
        with open(tmp, 'r') as f:
            text = f.read()
        parser = configparser.ConfigParser()
        parser.read_string(text)
        # assertion to check default content of userInfo file
        self.assertEqual(len(parser['info']), 2)        
        self.assertEqual(parser['info']['name'], '')
        self.assertEqual(parser['info']['email'], '')
        # test for sub directories
        # branches
        tmp = os.path.join(tmp_path, 'branches')
        tmp_files = os.listdir(tmp)
        # assertion to check if branches dir is empty
        self.assertEqual(len(tmp_files), 0)
        # objects
        tmp = os.path.join(tmp_path, 'objects')
        tmp_files = os.listdir(tmp)
        # assertion to check if objects dir is empty
        self.assertEqual(len(tmp_files), 0)
        # refs
        tmp = os.path.join(tmp_path, 'refs')
        tmp_files = os.listdir(tmp)
        # assertion to check if refs dir has two subdirs
        self.assertEqual(len(tmp_files), 2)
        for f in tmp_files:
            x = os.path.join(tmp, f)
            t = os.listdir(x)
            self.assertEqual(len(t), 0)
        # deleting the test directory
        os.system('rm -rf ' + path)


    # testcase: Non empty directory
    def test_init_2(self):
        dest = './test/testFiles/init'
        if not os.path.exists(dest):
            os.makedirs(dest)

        print('\nTestCase 2')
        print('Case: Non-empty directory')
        print('--------------\n')
        path = dest+'/'+ 'testDir'
        os.makedirs(path)
        os.makedirs(os.path.join(path, 'dir1'))
        with open(path + '/' + 'file1.txt', 'w') as f:
            f.write('Hello World!')
        with open(path + '/' + 'dir1' + '/' + 'file2.txt', 'w') as f:
            f.write('Hello world! inside dir1')
        # calling the function to be tested
        repo_create(path)
        files = os.listdir(path)
        # assertion to ensure .vcs directory is created
        self.assertIn('.vcs', files, msg=".vcs is not created")
        tmp_path = os.path.join(path, files[0])
        files = os.listdir(tmp_path)
        # assertion to ensure number of files inside .vcs is 7
        self.assertEqual(len(files), 7)
        # assertion to ensure if HEAD exist in .vcs dir
        self.assertIn('HEAD', files, msg="HEAD is not created")
        # assertion to ensure if 'branches directory is created
        self.assertIn('branches', files, msg="branches dir is not created")
        # assertion to ensure if config file is created
        self.assertIn('config', files, msg="config is not created")
        # assertion to ensure if description file is created
        self.assertIn('description', files, msg="description is not created")
        # assertion to ensure if objects dir is created
        self.assertIn('objects', files, msg="objects dir is not created")
        # assertion to ensure if refs dir is created
        self.assertIn('refs', files, msg="refs dir is not created")
        # assertion to ensure if userInfo file is created
        self.assertIn('userInfo', files, msg="userInfo files is not created")
        # tests for files
        # HEAD file
        tmp = os.path.join(tmp_path, 'HEAD')
        with open(tmp, 'r') as f:
            text = f.read()
        # assertion to check if default content of HEAD file
        self.assertEqual(text, 'ref: refs/heads/master\n')
        # description
        tmp = os.path.join(tmp_path, 'description')
        with open(tmp, 'r') as f:
            text = f.read()
        # assertion to check if default content of description file
        self.assertEqual(text, 'Unnamed repository; edit this desscription to name the repository\n')
        # config
        tmp = os.path.join(tmp_path, 'config')
        with open(tmp, 'r') as f:
            text = f.read()
        parser = configparser.ConfigParser()
        parser.read_string(text)
        # assertion to check default content of config file
        self.assertEqual(len(parser['core']), 3)
        self.assertEqual(parser['core']['repositoryformatversion'], '0')
        self.assertEqual(parser['core']['filemode'], 'false')
        self.assertEqual(parser['core']['bare'], 'false')
        # userInfo
        tmp = os.path.join(tmp_path, 'userInfo')
        with open(tmp, 'r') as f:
            text = f.read()
        parser = configparser.ConfigParser()
        parser.read_string(text)
        # assertion to check default content of userInfo file
        self.assertEqual(len(parser['info']), 2)        
        self.assertEqual(parser['info']['name'], '')
        self.assertEqual(parser['info']['email'], '')
        # test for sub directories
        # branches
        tmp = os.path.join(tmp_path, 'branches')
        tmp_files = os.listdir(tmp)
        # assertion to check if branches dir is empty
        self.assertEqual(len(tmp_files), 0)
        # objects
        tmp = os.path.join(tmp_path, 'objects')
        tmp_files = os.listdir(tmp)
        # assertion to check if objects dir is empty
        self.assertEqual(len(tmp_files), 0)
        # refs
        tmp = os.path.join(tmp_path, 'refs')
        tmp_files = os.listdir(tmp)
        # assertion to check if refs dir has two subdirs
        self.assertEqual(len(tmp_files), 2)
        for f in tmp_files:
            x = os.path.join(tmp, f)
            t = os.listdir(x)
            self.assertEqual(len(t), 0)     

if __name__ == "__main__":
    unittest.main()