# version-control-system
Version control system implemented in python

## TODO

- [X] vcs init --> command to initialize a vcs directory in a empty repository
- [X] vcs hash-object --> command to create object-ID of a file, commit etc and optionally store it in database/memory disk.
- [X] vcs cat-file  --> command to create appropiate vcs python object (deserialize) from serialized vcs objects stored in files
- [ ] vcs commit --> function to form commit and write it in log
- [ ] vcs log --> function to get commit history


## List of commands

- ### vcs init
    ```
    command format: vcs init <directory path>
    ```  
    This command helps to convert a directory to a repository by creating a vcs subdirectory. vcs subdirectory is named as .vcs and it contains all the commit objects, blobs, tree objects and configuration information. Thus, .vcs directory stores all the changes made in the working tree of the repository. All the commands use the data available in .vcs directory to perform approiate action.

    #### Directory structure

    root (of directory)  
    |  
    |_ _ working tree files/sub directories  
    |  
    |_ _ .vcs (vcs directory)  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|_ _ config (file which stores configuration info which is used by vcs program)  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|_ _ HEAD (file which stores the location of the object storing the latest commit)  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|_ _ objects (directory --> holds all the objects which are serialized and stored in memory)  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|_ _branches (directory)  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|_ _ refs (directory)  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|    |  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|    |_ _ tags (directory)  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|    |  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|    |_ _ heads (directory)  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|_ _ description (file which stores the description of the repository)  
    
- ### vcs hash-object
    ```
    command format: vcs hash-object [-w] [-t TYPE] FILE
    ```  
    This command reads a file and computes the hash of the content of the file.
    if -w flag is provided, then the file is content of the file is converted to a vcs object which is then serialized and then compressed and then stored in the .vcs/objects directory.

    #### Types of objects:
    - **Blob**: These objects are the common type of objects and contents of file in working directory and some other files are stored in such objects.
    - **commit**: These objects store the commit information.
    - **tree**: These objects store the tree information.
    - **tag**: These objects store the tag data.

    Every object which is serialized and stored as the file in the directory .vcs/object follows a generic format.
    The format is:  
    ```
    <header> + <whitespace> + <object size> + <null separator (0x00)> + <byte string of the object>
    ```
    The content of the file is in byte string format.

- ### vcs cat-file
    command format: vcs cat-file TYPE OBJECT
    
    This command reads a file storing the serialized object and then deserializes it into a python object of class TYPE.
    This command does the opposite of what command hash-object does. While deserializing, this command checks if object size matches the size mentioned in file, thus, data malformation is detected.