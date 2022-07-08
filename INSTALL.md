# SCSC Smart Contract Scam Checker

The SCSC Smart Contract Scam Checker consists of a backend and a frontend application.


## Backend application installation
Please follow the instructions to install the backend services necessary to run SCSC:  
(The instructions are tested on a raw Ubuntu 20.04 installation)  

1. Install python, pip and git with the following command:  
    $ ```sudo apt install python3 python3-pip```  

2. Clone the SCSC github repository and change directory to the project folder:  
    $ ```git clone https://github.zhaw.ch/ackerpas/eth-scam-checker.git```  
    $ ```cd eth-scam-checker```  

3. Install the necessary python requirements with the following command:  
    $ ```pip3 install -r requirements.txt```  

4. Ensure that the python installed programs are inside the PATH variable, otherwise add them:  
    $ ```export PATH=$PATH:/home/user/.local/bin```  

5. Install the necessary solc compiler versions using solc-select (this might take a while):  
    $ ```solc-select install all```  

6. Install mongodb as the backend database (according to https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/)  
    $ ```wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -```  
    $ ```echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list```    
    $ ```sudo apt-get update```  
    $ ```sudo apt-get install -y mongodb-org```  
    $ ```sudo systemctl start mongod```  
    $ ```sudo systemctl enable mongod```  

7. Initialize the mongodb collections with an index to improve future lookups:    
    $ ```python3 initialize_db.py```  

8. Launch the SCSC backend application:  
    $ ```python3 mainapp.py```  

9. Run the monitor tester to verify if tokens get processed properly (optional):  
    $ ```python3 smoke_test.py```  

In case of questions please create a github issue or message the developers.  
(This is the ZHAW internal repository, which is already provisioned with a working .env file containing the students API keys, please don't run multiple instances for a long time)

## Frontend application installation
Please follow the instructions to install the backend services necessary to run SCSC:  
(The instructions are tested on a raw Ubuntu 20.04 installation)

1. Change directory to the frontend folder:  
    $ ```cd frontend```
2. Install nvm according to https://github.com/nvm-sh/nvm#installing-and-updating with the following one-liner:  
    $ ```curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash``` 
3. Either close and reopen the current shell or run the following command:  
    $ ```export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"```    
4. Install node using nvm:  
    $ ```nvm install node```  
5. Install yarn and serve using the newly installed npm:  
    $ ```npm install --global yarn```  
    $ ```npm install -g serve```
6. Use yarn to install dependencies and build the frontend application:  
    $ ```yarn install```  
    $ ```yarn build```  
    $ ```yarn global add serve```
7. Launch the application with serve:  
    $ ```serve -s build -l 8080```

## Restoring Test databases

During the development, the collected tokens were stored into the mongodb database.  
These databases are attached to this repository, to provide initial data for the applications and is necessary for the statistical tools to work propperly.  
To restore the databases, use the following instructions:  
1. Change into the repository root folder:  
    cd ```eth-scam-checker```
2. Restore the monitor database:  
    $ ```mongorestore data/mongodb_export/```  