# ScrollGuard Sanction Screening System

## Prerequisites
Make sure you have installed the following on your machine.
- [Python](https://www.python.org/downloads/)
- [MongoDB](https://www.mongodb.com/)
- [Git](https://git-scm.com/)

## Setting-up
1. Create your project directory.
`mkdir scrollguard`
`cd scrollguard`

2. Clone the repository.
`git clone https://github.com/imjbmkz/ScrollGuard.git`

3. Create a virtual environment. Activate it.
`python3 -m venv env`
`source env/bin/activate`

4. Install required packages.
`pip install -r requirements.txt`

5. Add the following environment variables to the activate file.
`MONGO_HOST=mongodb://mongodb0.example.com:28015 # for local MongoDB server`
`MONGO_CLIENT=mongodb://mongodb0.example.com:28015 # for cloud MongoDB server`

6. Run `configure.py` to add basic configuirations to MongoDB.
`python3 configure.py`