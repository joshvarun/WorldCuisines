# World Cuisines

World Cuisines is a project for Udacity's Full Stack Web Developer Nano degree. 

This application provides a list of items within a variety of categories (Cuisines) as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items in the cuisines.

![alt text](https://i.postimg.cc/zDKgG0Q3/Screenshot-2019-01-19-at-11-49-06-AM.png)


## Getting Started

### Prerequisites
1. [Vagrant](https://www.vagrantup.com)
2. [Python](https://www.python.org/downloads/)
3. [VirtualBox](https://www.virtualbox.org)
4. [SQLAlchemy](https://www.sqlalchemy.org)

## Installation & Setup

1. Install [Vagrant](https://www.vagrantup.com) and [VirtualBox](https://www.virtualbox.org)
2. Download or Clone [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) repository.
3. Clone this repository into a directory 

```bash
$ git clone https://github.com/joshvarun/WorldCuisines.git
```

#### Launching the Virtual Machine:

1. Launch the Vagrant VM inside Vagrant sub-directory in the downloaded `fullstack-nanodegree-vm` repository using command:
  ```bash
$ vagrant up
```
Note: This might take some time depending on the speed of your internet connection. It downloads a linux vm from the internet.
2. Then Log into this using command:
```bash  
$ vagrant ssh
```
Change directory `/vagrant` and look around with `ls`.

#### Setting up the database
The database in the repo is already populated with sample data. However, in case you need a fresh repository, please run 

```bash
$ python database_setup.py
```

#### Running the project
Run the application.py file to setup the web-server on localhost:8000

```bash
$ python application.py
```
#### Google Client ID - client_secrets.json

To run this project, create a project on the Google Developer Console, & create an OAuth2.0 Credential for it.

Add authorized domains & redirect urls, download the json. Rename the downloaded json as ```client_secrets.json``` & place it in the same folder as ```application.py```

## Author
* **Varun Joshi** - *Initial work* - [joshvarun](https://github.com/joshvarun)

## Credits
1. Background Image, Cuisine & Item Images taken from [Pexels.com](https://www.pexels.com)
