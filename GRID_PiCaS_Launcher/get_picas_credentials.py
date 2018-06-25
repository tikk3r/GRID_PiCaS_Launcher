import datetime
from os.path import expanduser,isfile
from os import environ, chmod

class picas_cred():

    def __init__(self,source=None,usr=None,pwd=None,dbn=None):
        if source:
            self.get_picas_creds_from_file(pic_file=source) 
        elif usr==None or pwd==None and dbn!=None:
                if isfile(expanduser('~/.picasrc')):
                    self.get_picas_creds()
                else:
                    self.get_picas_creds_from_env()
        else:
            self.user=usr
            self.password=pwd
            self.database=dbn


    def get_picas_creds_from_file(self,pic_file='~/.picasrc'):
        with open(expanduser(pic_file),'r') as file:
            print(datetime.datetime.now(), "picas_credentials: Parsing user credentials from", expanduser(pic_file))
            for line in file:
                if line.startswith("user"):
                    self.user = line.split('=')[1].strip()
                if line.startswith("password"):
                    self.password = line.split('=')[1].strip()
                if line.startswith("database"):
                    self.database = line.split('=')[1].strip()
    
    def get_picas_creds_from_env(self):
        try:
            self.user=environ['PICAS_USR']
            self.password=environ['PICAS_USR_PWD']
            self.database=environ['PICAS_DB']
        except KeyError:
            print("PICAS Variable not in ENV!") 
   
    def get_picas_creds(self):
        if not environ.get('PICAS_USR') and not environ.get('PICAS_USR_PWD') and not environ.get('PICAS_DB'):
            return self.get_picas_creds_from_env()
        else:
            return self.get_picas_creds_from_file()
    
    def put_picas_creds_in_env(self,picas_db=None):
#        creds=self.get_picas_creds()  #Possibly breaks
        if picas_db:
            self.database=picas_db
            creds['PICAS_DB']=picas_db
        environ['PICAS_USR']=self.user
        environ['PICAS_USR_PWD']=self.password
        if self.database:
            environ['PICAS_DB']=self.database
        else: environ['PICAS_DB']=self.database
        return #self.get_picas_creds()

    def put_creds_in_file(self,pic_file="~/.picasrc"):
        with open(expanduser(pic_file),'w') as file:
            file.write("user="+str(self.user)+"\n")
            file.write("password="+str(self.password)+"\n")
            file.write("database="+str(self.database)+"\n")
        chmod(expanduser(pic_file),384)

    def return_credentials(self):
        return {'user':self.user, 'password':self.password,'database':self.database}
        
