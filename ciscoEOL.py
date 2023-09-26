#!/usr/bin/python

import getpass,requests
import pandas as pd
from colorama import Fore,init

class classCiscoSupport():

    #Initialize Colorama
    init()

    #Set base url for project
    base_url = "https://apix.cisco.com/supporttools/eox/rest/5/"

    def __init__(self):
        """
        Prompt for credentials for Cisco Support RestAPI.
        """
        self.headers = self.get_headers()
        self.token = self.get_token()

    def get_headers(self):
        """
        Creates the login headers for Cisco Support RestAPI.
        Inputs: 
        Outputs:
            - headers
        """
        #Set restAPI header information into dictionary
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            }
        return (headers)    
         
    def get_token(self):
        """
        Retrieves a token for Cisco Support RestAPI.
        Inputs: client_id, client_secret
        Outputs:
            - token
        """
        #set url
        url = "https://id.cisco.com/oauth2/default/v1/token"
        
        print("=" * 50)
        usr=input("Please enter your Cisco Support Client ID: ")
        pwd=getpass.getpass("Please enter your Cisco Support Client Secret: ")

        #Set data.  Authentication is required to get a token
        data = {
            "grant_type": "client_credentials",
            "client_id" : usr,
            "client_secret" : pwd,
        }

        #run api call
        try:
            resp = requests.post(url,params=data,headers=self.headers, verify=True)
            #check for HTTP codes other than 200
            if resp.status_code == 200:
                token = str(resp.json()['access_token'])
                self.headers["Token"] = token
                #print(f'{Fore.CYAN}I GOT A TOKEN!!!{Fore.RESET}')
                #print ("token = " + token)
                return (token)
            else:
                print (f'Get token failed! - {str(resp.text)}')
                return (f'Get token failed! - {str(resp.text)}')
        except Exception as e:
            print(str(e))
            return (str(e))

    def get_eol(self):
        """
        Retrieves EOL dates by serial from Cisco Support RestAPI.
        Inputs: token
        Outputs:
        """
        #set url
        url = self.base_url + "EOXBySerialNumber/1/"

        #set the headers and include token information received from get_token
        tokenheaders = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + str(self.token)
            }

        #print("=" * 50)
        defaultfile = "eolserials.csv"
        serialfile=input(f"Please choose file [{defaultfile}]: ").strip() or defaultfile

        #open CSV file and replace new lines wiht commas as required by Cisco Support ResAPI
        
        #with open(serialfile,'r') as f:
        #    deviceserial = list(line for line in (l.strip() for l in f) if line)
        #    deviceserial = f.read().replace('\n',',')
        #    deviceserial = f.read().replace('\n',',').strip()
        #print (deviceserial)

        df = pd.read_csv(serialfile, header=None, nrows=20)
        print ('Dataframe shape:',df.shape)

        df = df.to_string(header=False, index=False)
        deviceserial=df.replace('\n',',')
        #run api call
        try:
            resp = requests.get(url+str(deviceserial),headers=tokenheaders, verify=True)
            
            #check for HTTP codes other than 200
            if resp.status_code == 200:
                #establish the base index of the json output
                eoxrecord=resp.json()['EOXRecord']

                #create dictionary for table
                my_dict = {'deviceserial':[],'EOLDate':[]}
                #my_dict = {'deviceserial':[],'EOLDate':[],'EOL Product ID':[],'Product Description':[], 'Migration Product':[], 'Migration Strategy':[]}
                
                #loop through the base index from the total length of output
                for i in range(len(eoxrecord)):
                    #establish variables from indexes of records of interest
                    deviceid=eoxrecord[i]['EOXInputValue']
                    eoldate=eoxrecord[i]['LastDateOfSupport']['value']
                    eolproductid=eoxrecord[i]['EOLProductID']
                    #piddescription=eoxrecord[i]['ProductIDDescription']
                    #migration=eoxrecord[i]['EOXMigrationDetails']['MigrationProductName']
                    #migrationstrategy=eoxrecord[i]['EOXMigrationDetails']['MigrationStrategy']
                    
                    #if the product id is empty, it is either not found or not EOL
                    if eolproductid == "":
                        #check the error id to see if not found or EOL
                        eolerror=eoxrecord[i]['EOXError']['ErrorID']
                        #SSA_ERR_015 is not found.  SSA_ERR_026 is not EOL
                        if eolerror == "SSA_ERR_015":
                            #pass to leave off the entries.  If yo want to write a column, reverse the comments
                            #pass
                            my_dict['deviceserial'].append(deviceid)
                            my_dict['EOLDate'].append(eoldate)
                            #my_dict['EOL Product ID'].append(eolproductid)
                            #my_dict['Product Description'].append(piddescription)
                            #my_dict['Migration Product'].append(migration)
                            #my_dict['Migration Strategy'].append(migrationstrategy)
                        else:
                            #if not EOL then the product ID will be listed in this index
                            eolproductid=eoxrecord[i]['EOXError']['ErrorDataValue']
                    #if product id is not empty, that means it's EOL
                    else:
                        #if deviceid has a comma split it.  some entries for modules show up with both serials
                        x = deviceid.split(",")
                        #loop through both serials and append both to dictionary with the same eol date
                        for i in x:
                            my_dict['deviceserial'].append(i)
                            my_dict['EOLDate'].append(eoldate)
                            #my_dict['EOL Product ID'].append(eolproductid)
                            #my_dict['Product Description'].append(piddescription)
                            #my_dict['Migration Product'].append(migration)
                            #my_dict['Migration Strategy'].append(migrationstrategy)
                
                #define the pandas dataframe
                df=pd.DataFrame(my_dict)
                print (df)
                #convert this mother to CSV
                df.to_csv('eolreport.csv', index=False)

            #if the response code isn't 200 then something went wrong        
            else:
                print ("Login failed! -" + str(resp.text))
                return ("Login failed! -" + str(resp.text))
        except Exception as e:
            print(str(e))
            return(str(e))

ca = classCiscoSupport()
ca.get_eol()