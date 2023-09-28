#!/usr/bin/python

import getpass,requests,os
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
        #comment out if you want to test hard coded
        usr=input("Please enter your Cisco Support Client ID: ")
        pwd=getpass.getpass("Please enter your Cisco Support Client Secret: ")
        #uncomment to hard code for testing
        #usr="putyourclientidhere"
        #pwd="putyoursecrethere"

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
                
        #read CSV in chunks of 20 which is the maximum allowed by Cisco Support API
        chunksize = 20 ** 1
        readfile=pd.read_csv(serialfile, header=None)
        #get total length
        rowcount=len(readfile.index)
        
        #open CSV file and replace new lines with commas as required by Cisco Support RestAPI
        with pd.read_csv(serialfile, header=None, chunksize=chunksize) as reader:
            #creates a header on the output csv on the first pass
            writeheader = True
            count = 0
            for chunk in reader:

            #read only the first 20 lines
            #df = pd.read_csv(serialfile, header=None, nrows=20)
                chunkamount = chunk.shape
                progressnumber = count + chunkamount[0]
                print ('Progress: [',progressnumber,'/',rowcount,']')
                #remove whitespaces
                df = chunk.to_string(header=None, index=False).replace(' ','')
                deviceserial=df.replace('\n',',')
                #print (deviceserial)

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
                            if eolproductid == "" or eolproductid == None:
                                #check the error id to see if not found or EOL
                                eolerror=eoxrecord[i]['EOXError']['ErrorID']
                                #SSA_ERR_015 is not found, SSA_ERR_010 is invalid
                                if eolerror == "SSA_ERR_015" or eolerror == "SSA_ERR_010":
                                    #pass to leave off the entries.  If you want to write a column, comment out pass and reverse the other comments
                                    pass
                                    #my_dict['deviceserial'].append(deviceid)
                                    #my_dict['EOLDate'].append(eoldate)
                                    #my_dict['EOL Product ID'].append(eolproductid)
                                    #my_dict['Product Description'].append(piddescription)
                                    #my_dict['Migration Product'].append(migration)
                                    #my_dict['Migration Strategy'].append(migrationstrategy)
                                #SSA_ERR_026 is not EOL so just find the product id
                                elif eolerror == "SSA_ERR_026":
                                    #if not EOL then the product ID will be listed in this index
                                    eolproductid=eoxrecord[i]['EOXError']['ErrorDataValue']
                                else:
                                    print ("Retrieval failed! -" + str(resp.text))
                                    
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
                        #convert this mother to CSV and writes header if true
                        df.to_csv('eolreport.csv', mode='a', index=False, header=writeheader)
                        #sets header value to false so it doens't write again
                        writeheader = False

                    #if the response code isn't 200 then something went wrong        
                    else:
                        print ("Retrieval failed! -" + str(resp.text))
                        return ("Retrieval failed! -" + str(resp.text))
                except Exception as e:
                    print(str(e))
                    return(str(e))
                #add completed amount to chunk count
                count = count + chunkamount[0]

ca = classCiscoSupport()
ca.get_eol()