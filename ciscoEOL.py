#!/usr/bin/python

import getpass,requests,json,os
import pandas as pd
from colorama import Fore,Style,init

class classNetbrain():
    """
    This class is used to perform all functions from within NetBrain RestAPI.
    The restAPI user and URL are hard coded in the env file and used in many functions.
    """
    #Initialize Colorama
    init()
    
    #Load environment variable from .env file in project root folder
    #load_dotenv()
    
    #set NetBrain login information from environment variable file
    user = os.getenv('NETBRAIN_USER')
    pwd = os.getenv('NETBRAIN_PASSWORD')
    authentication_id = os.getenv('NETBRAIN_AUTHENTICATION_ID')
    tenant = os.getenv('NETBRAIN_TENANT')
    domain = os.getenv('NETBRAIN_DOMAIN')
    server_url = os.getenv('NETBRAIN_BASE_URL')

    def __init__(self):
        """
        Runs every call to class NetBrain.  Includes get_headers(), get_token(), and set_domain().
        Inputs:
        Outputs:
            - headers
            - set_domain
        """
        #Every call will need headers, a token, and a domain set
        self.headers = self.get_headers()
        #comment out self.token and call separately if running multiple calls
        #self.token = self.get_token()
        self.set_domain = self.set_domain()

    def get_headers(self):
        """
        Creates the login headers for NetBrain RestAPI.
        Inputs: 
        Outputs:
            - headers
        """
        #Set restAPI header information into dictionary
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            }

        return (headers)
    
    def get_token(self):
        """
        Retrieves a token for NetBrain RestAPI.
        Inputs:
            - username
            - password
            - authentication_id
        Outputs:
            - token
        """
        #set url
        url = self.server_url + "V1/Session"
        
        #Set data.  Authentication_id is required for external (TACACS) users only
        data = {
            "username": self.user,
            "password": self.pwd,
            "authentication_id": self.authentication_id
        }
        #run api call
        try:
            resp = requests.post(url,data=json.dumps(data),headers=self.headers, verify=True)
            #check for HTTP codes other than 200
            if resp.status_code == 200:
                #find the token index
                token = resp.json()["token"]
                #place token in the headers
                self.headers["Token"] = token
                print(f'{Fore.CYAN}I GOT A NETBRAIN TOKEN!!!{Fore.RESET}')
                return (token)
            else:
                return (f'Get token failed! - {str(resp.text)}')
        except Exception as e:
            return (str(e))
        
    def set_domain(self):
        """
        Retrieves a token for NetBrain RestAPI.
        Inputs:
            - tenant: NetBrain tenant
            - domain: NetBrain domain
            - token
        Outputs:
        """
        #set url
        url = self.server_url + "V1/Session/CurrentDomain"
        
        #set data
        data = {
            "tenantId": self.tenant,
            "domainId": self.domain
        }
    
        #run api call
        try:
            resp = requests.put(url,data=json.dumps(data),headers=self.headers, verify=True)
            #check for HTTP codes other than 200
            if resp.status_code == 200:
                pass
                #result = resp.json()
            else:
                return ("Login failed! -" + str(resp.text))
        except Exception as e:
            return(str(e))
            
    def logout(self):
        """
        Ensure you logout of each session.  Once you logout you will need a new token.
        Inputs:
            - token
        Outputs:
        """
        #set url
        url= self.server_url + "V1/Session"
        data = {
            "token": self.headers["Token"]
        }
        try:
            resp = requests.delete(url,data=json.dumps(data),headers=self.headers, verify=True)
            #check for HTTP codes other than 200
            if resp.status_code == 200:
                print(f'{Fore.CYAN}I LOGGED OUT OF NETBRAIN!!!{Fore.RESET}')
                return (resp.text)
            else:
                print ("Session logout failed! -" + str(resp.text))
        except Exception as e:
            return(str(e))
    
    def get_all_devices_and_attributes(self):
        """
        Gets a list of all successfully discovered devices and attributes
        Inputs:
            - headers
        Outputs: 
            - result - json output of devices and attributes
        """
        #set the url for device and attributes
        deviceurl = self.server_url + "V1/CMDB/Devices"
        moduleurl = self.server_url + "V1/CMDB/Modules/Attributes"
        #create a list to append json output
        rawList = []
        print (f'{Style.BRIGHT}Preparing Device and Module List...{Style.NORMAL}')

        """
        ===============================================================
        THIS SECTION IS TO RETURN THE DEVICE ATTRIBUTES WITHOUT MODULES
        ===============================================================
    
        This section will gather the device attributes without the modules.

        Skip is the number of records to skip on the call, so after the first 50 are processed, skip must be increased 50. 
        Count is the number of records.  Netbrain can only return 50 entries per page, so count is always 50.
        This continues the loop while the page count is 50.  Skip will keep increasing and eventually count will be less than 50
        when there are not many records remaining.
        """
        skip = 0
        count = 50
        #run api call to get list of devices
        try:
            while count == 50:
                #required parameters
                data = {
                    "version": 1,
                    "skip": skip,
                    "fullattr": 1
                }
                #run the main device query API calls
                resp = requests.get(deviceurl, params=data, headers=self.headers, verify=True)
                #Check for HTTP code other than 200. If 200 then proceed
                if resp.status_code == 200:
                    #set the result at the root index of devices.  All attributes are under this index
                    result = resp.json()['devices']
                    #set the count as the number of results.  This will be at 50 until there are few records remaining
                    count = len(result)
                    #set the skip to the length of results so Netbrain can display the next set
                    skip = skip + count
                    #uncomment to create a shorter list for testing
                    #if skip == 100:
                    #    break
                    
                    """
                    ===============================================================
                    THIS SECTION IS TO RETURN THE DEVICE MODULE ATTRIBUTES
                    ===============================================================

                    This section will gather the device module attributes if they exist.  The serials and other module information 
                    is retrieved by a separate api call with a parameter of hostname.
                    """
                    #loop through devices result to display sub-attributes
                    for i in result:
                        #define hostname variables
                        hostname = i['name']
                        #define parameters for module attribute API call. hostname is required
                        data = {
                            "hostname": hostname
                        }
                        #run the module attribute API calls
                        resp = requests.get(moduleurl, params=data, headers=self.headers, verify=True)
                        #Check for HTTP code other than 200. If 200 then proceed
                        if resp.status_code == 200:
                            #create a variable named result
                            result = resp.json()
                            #if the attribute index exists, then proceed
                            if resp.json()['attributes']:
                                #exclude hostname index while cycling through results. This isn't needed
                                #but the attributes root key needs to be preserved in the json
                                exclude_key = "hostname"
                                #append the module json to rawList and delete the hostname key
                                #this will add the "attributes" key to the existing dictionary above it
                                if exclude_key in result:
                                    del result[exclude_key]
                                    #update the previous json with the module attribute json output
                                    i.update(result)
                                    #append the results of device and module to the list
                                    rawList.append(i)
                            #if there are no attributes for the device then continue without action
                            else:
                                #append just the device
                                rawList.append(i)
                                continue
                        #if HTTP code for module attributes is not 200
                        else:
                            result = "Get Devices Failed - Status Code: " + str(resp.status_code) + ", Response: " + str(resp.text)
                            #print (result)
                            return (result)
                #if HTTP code for devices is not 200
                else:
                    result = "Get Devices Failed - Status Code: " + str(resp.status_code) + ", Response: " + str(resp.text)
                    #print (result)
                    return (result)
        except Exception as e:
            print (str(e))

        #sort the list by device name
        sortedList = sorted(rawList, key=lambda x: x['name'].lower())
        #save the result as json output
        result = json.dumps(sortedList, indent=4, sort_keys=False)
        return (result)
    
    def add_eol_attributes(self):
        """
        Adds EOL attributes of devices and modules from eolreport
        Inputs:
            - headers
        Outputs:
            - result
        """

        #configure the url to query attributes
        url = self.server_url + "V1/CMDB/Devices/Attributes"
        #set parameters necessary for api call (Netbrain API defined)
        eolreport = '~/Desktop/eolreport.csv'

        #convert the list of serials to a pandas dataframe
        df = pd.read_csv(eolreport)

        print (f'{Style.BRIGHT}Preparing Netbrain Upload of Device and Module End-of-Life Attribute...{Style.NORMAL}')
        #loop through dataframe and save values for each column
        count = 0
        for index,row in df.iterrows():
            #uncomment to limit API calls
            #if count == 3:
            #    break

            #set body values for API call
            hostname = row['hostname']
            moduleName = row['modulename']
            deviceserial = row['deviceserial']
            attributeValue = row['EOLDate']

            #set eol attribute name depending on if row is a device or module
            if pd.isna(moduleName) or moduleName == '':
                attributeName = "deviceeol"
                #define parameters for module attribute API call.
                data = {
                    "hostname": hostname,
                    "attributeName": attributeName,
                    "attributeValue": attributeValue
                }  
                #set the url for device and attributes
                url = self.server_url + "V1/CMDB/Devices/Attributes"
            else:
                attributeName = "moduleeol"
                #define parameters for module attribute API call.
                data = {
                    "hostname": hostname,
                    "attributeName": attributeName,
                    "attributeValue": attributeValue,
                    "moduleName": moduleName
                }  
                #set the url for module and attributes
                url = self.server_url + "V1/CMDB/Modules/Attributes"
            
            #make the API call
            try:
                resp = requests.put(url,data=json.dumps(data),headers=self.headers, verify=True)
                #check for HTTP codes other than 200
                if resp.status_code == 200:
                    pass
                else:
                    print ("Setting Attribute Failed! -" + str(resp.text))
            except Exception as e:
                return(str(e))
            #uncomment to limit api calls
            #count = count + 1

class classCiscoSupport():
    """
    This class is used to perform all functions from within Cisco EOL API.
    The restAPI user and URL are hard coded in the env file and used in many functions.
    """

    #Initialize Colorama
    init()

    #Load environment variable from .env file in project root folder
    #load_dotenv()
    
    #set NetBrain login information from environment variable file
    usr = os.getenv('CISCOEOL_USER')
    pwd = os.getenv('CISCOEOL_PASSWORD')
    eolserialfilename = os.getenv('CISCOEOL_SERIALS')
    eolreportfilename = os.getenv('CISCOEOL_REPORT')

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
        #set the credentials
        usr=self.usr
        pwd=self.pwd

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

    def get_eol(self, inventoryfilename):
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

        print("=" * 50)
        #set the json inventory filename
        inventory = inventoryfilename       
        #create a blank list to store variable information
        serialList = []
        hostnameList = []
        
        #open the inventory and rename as variable file
        with open(inventory, 'r') as file:
            #load the dictionary file in json
            jsonfile = json.load(file)
        
        #loop through the results of the json
        for i in jsonfile:
            #extract the variables desired
            devicesn = i['sn']
            devicename = i['name']

            """
            Allowed variable list:
            "name": "hostname",
            "mgmtIP": "10.10.10.1",
            "mgmtIntf": "Loopback0",
            "subTypeName": "Cisco IOS Switch",
            "vendor": "Cisco",
            "model": "WS-C3650-48PD",
            "ver": "16.12.07",
            "sn": "FTX12345J2343",
            "site": "My Network\\Remote\\Location",
            "loc": "SNMP Location Information",
            "contact": "",
            "mem": "813753120",
            "assetTag": "",
            "layer": "",
            "descr": "",
            "oid": "1.3.6.1.4.1.9.1.2066",
            "driverName": "Cisco IOS Switch",
            "fDiscoveryTime": "2019-07-03T15:04:05Z",
            "lDiscoveryTime": "2023-12-09T07:08:35Z",
            "assignTags": "",
            "hasBGPConfig": true,
            "hasEIGRPConfig": false,
            "hasIPv6Config": true,
            "hasISISConfig": false,
            "hasMulticastConfig": false,
            "hasOSPFConfig": false,
            "hasQoSConfig": true,
            "policyGroup": "",
            "BPE": "",
            "OTV": "",
            "VPLS": "",
            "VXLAN": "",
            "cluster": "",
            "l3vniVrf": "",
            "listprice": "",
            "_nb_features": "",
            "bgpNeighbor": "",
            "ap_mode": "",
            "APMeshRole": "",
            "snmpName": "",
            "bldgCode": "ABC",
            "ciscoContractId": "",
            "ciscoBasePid": "",
            "roomnumber": "100",
            "campus": "Remote",
            "replacementmodel": "",
            "techlayer": "Wired",
            "deviceeol": "1/1/28",
            "component": "D-Gen",
            "function": "Distribution Layer",
            "team": "team",
            "id": "71a7e2cc-7dc0-4a30-9b5e-0f53334fa681",
            "attributes": {
            """

            #append the serial number to serialList
            serialList.append([devicesn,devicename])

            if "attributes" in i:
                #loop through the 'attributes' and extract values
                for x in i['attributes'].values():
                    sn = x['sn']
                    modulename = x['name']

                    """ Allowed variable list:
                    "attributes": {
                        "c36xx Stack": {
                            "name": "c36xx Stack",
                            "type": "WS-C3650-48FD-E",
                            "ports": "",
                            "sn": "FDO2013E1AC",
                            "hwrev": "V03",
                            "fwrev": "",
                            "swrev": "",
                            "descr": "",
                            "ciscoContractId": "",
                            "ciscoBasePid": "",
                            "moduleeol": "10/31/26",
                            "techlayer": "Wired",
                            "component": "D-Gen",
                            "function": "Distribution Layer",
                            "team": "NS-DNF"
                        },
                        "Gi1/1/1": {
                            "name": "Gi1/1/1",
                            "type": "GLC-LH-SMD",
                            "ports": "",
                            "sn": "AGA1728UBFJ",
                            "hwrev": "V01",
                            "fwrev": "",
                            "swrev": "",
                            "descr": "",
                            "ciscoContractId": "",
                            "ciscoBasePid": "",
                            "moduleeol": "",
                            "techlayer": "Wired",
                            "component": "Optic",
                            "function": "Misc Items",
                            "team": "NS-DNF"
                        },
                    """

                    #if serialnumber is blank or N/A continue without action
                    if str(sn) == "" or "N/A" in str(sn):
                        continue
                    #if serial is not blank or N/A
                    else:
                        #if the device serial number matches the module serial then don't append it
                        if devicesn == sn:
                            pass
                        else:
                            #append the module serial number and hostname to serials
                            serialList.append([sn,devicename,modulename])

        #convert the list of serials to a pandas dataframe
        df = pd.DataFrame(serialList)
        #if there are multiple comma-separated strings per cell, split them and put them on their own line
        #df = df[0].str.split(',', expand=True).stack().reset_index(level=1, drop=True).to_frame(0)
        df[0] = df[0].str.split(',')
        df = df.explode(0).reset_index(drop=True)
        # Drop lines containing "Serial:" or "MAC:"
        df = df[~df[0].str.contains('Serial:|MAC:', case=False, na=False)]
        #drop blanks in the serial number column
        #df = df.replace('', pd.NA).dropna()
        #drop blanks in the serial number first column only
        df = df.replace('', pd.NA).dropna(subset=[df.columns[0]])
        #sort alphabetically
        #df = df.sort_values(by=df.columns[0], key=lambda x: x.str.lower())

        #convert to csv without any headers or index numbers
        serialList = df.to_csv(self.eolserialfilename, header=None, index=False)
        #read CSV in chunks of 20 which is the maximum allowed by Cisco Support API
        chunksize = 20 ** 1
        readfile=pd.read_csv(self.eolserialfilename, header=None, lineterminator='\n')
        #get total length
        rowcount=len(readfile.index)
        
        #open CSV file, read only the first column, and replace new lines with commas as required by Cisco Support RestAPI
        with pd.read_csv(self.eolserialfilename, header=None, chunksize=chunksize) as serials:
            #creates a header on the output csv on the first pass
            writeheader = True
            count = 0
            #loop through chunks
            for chunk in serials:
                chunkamount = chunk.shape
                progressnumber = count + chunkamount[0]
                #show progress of entire rowcount
                print ('Progress: [',progressnumber,'/',rowcount,']')
                # print ("Column 1:")
                # print (chunk[0].tolist())
                # print ("Column 2:")
                # print (chunk[1].tolist())
                #remove whitespaces
                df = chunk[0].to_string(header=None, index=False).replace(' ','')
                #change newline to comma
                deviceserial=df.replace('\n',',')
                #print (deviceserial)

                #run api call
                try:
                    resp = requests.get(url+str(deviceserial),headers=tokenheaders, verify=True)
                    
                    #check for HTTP codes other than 200
                    if resp.status_code == 200:
                        #establish the base index of the json output
                        eoxrecord=resp.json()['EOXRecord']
                        #create an empty list for hostnames
                        #create dictionary for table
                        my_dict = {'hostname':[],'modulename':[],'deviceserial':[],'EOLDate':[]}
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
                                    #pass to leave off the entries
                                    pass
                                #SSA_ERR_026 is not EOL so just find the product id
                                elif eolerror == "SSA_ERR_026":
                                    #if not EOL then the product ID will be listed in this index
                                    eolproductid=eoxrecord[i]['EOXError']['ErrorDataValue']
                                    #if eolproductid is blank, then the device doesn't exist and should pass
                                    if eolproductid == "":
                                        pass
                                    #if the eolproductid is not blank, split the inputs by comma and append
                                    else:
                                        eoldate="Not Announced"
                                        x = deviceid.split(",")
                                        for i in x:
                                            #find the corresponding hostname that matches the serial in the chunk
                                            serialmatch = chunk[chunk[0] == i]
                                            hostname = serialmatch[1].values[0]
                                            modulename = serialmatch[2].values[0]
                                            #append values to dictionary
                                            my_dict['hostname'].append(hostname)
                                            my_dict['modulename'].append(modulename)
                                            my_dict['deviceserial'].append(i)
                                            my_dict['EOLDate'].append(eoldate)
                                else:
                                    print ("Retrieval failed! -" + str(resp.text))
                                    
                            #if product id is not empty, that means it's EOL
                            else:
                                #if deviceid has a comma split it.  some entries for modules show up with both serials
                                x = deviceid.split(",")
                                #loop through both serials and append both to dictionary with the same eol date
                                for i in x:
                                    #find the corresponding hostname and module name that matches the serial in the chunk
                                    serialmatch = chunk[chunk[0] == i]
                                    hostname = serialmatch[1].values[0]
                                    modulename = serialmatch[2].values[0]
                                    #append values to dictionary
                                    my_dict['hostname'].append(hostname)
                                    my_dict['modulename'].append(modulename)
                                    my_dict['deviceserial'].append(i)
                                    my_dict['EOLDate'].append(eoldate)
                                    #my_dict['EOL Product ID'].append(eolproductid)
                                    #my_dict['Product Description'].append(piddescription)
                                    #my_dict['Migration Product'].append(migration)
                                    #my_dict['Migration Strategy'].append(migrationstrategy)
                        
                        #define the pandas dataframe
                        df=pd.DataFrame(my_dict)
                        df_sorted = df.sort_values(by=df.columns[0])
                        print (f'{Fore.CYAN}{df}{Fore.RESET}')
                        #convert this to CSV and writes header if true
                        if os.path.isfile(self.eolreportfilename):
                            df_sorted.to_csv(self.eolreportfilename, mode='a', index=False, header=writeheader)
                        else:
                            df_sorted.to_csv(self.eolreportfilename, mode='w', index=False, header=writeheader)
                        #sets header value to false so it doens't write again
                        writeheader = False

                    #if the response code isn't 200 then something went wrong        
                    else:
                        print ("Retrieval failed! -" + str(resp.text))
                        return ("Retrieval failed! -" + str(resp.text))
                except Exception as e:
                    print(str(e))
                    return(str(e))
                #calculate completed amount to chunk count
                count = count + chunkamount[0]

#Begin the Work
netbrain = classNetbrain()
cisco = classCiscoSupport()

#run the Netbrain function to gather all devices from netbrain
#attributeList,serials,hostnames,tuplelist = netbrain.get_all_devices_and_attributes()
netbrain.get_token()
rawList = netbrain.get_all_devices_and_attributes()
#attributeList,tuplelist = netbrain.get_all_devices_and_attributes()
#log out of netbrain
#netbrain.logout()  

#create a file containing the json inventory from netbrain
inventoryfilename = '~/Desktop/lcm-fullinventory.json'
os.makedirs(os.path.dirname(inventoryfilename), exist_ok=True)
with open(inventoryfilename,'w') as f:
    print (rawList,file=f)

#run the commands to generate eol dates
cisco.get_eol(inventoryfilename)

#run the netbrain add attributes command
netbrain.add_eol_attributes()
netbrain.logout()  

print(f'{Fore.GREEN}Finished{Fore.RESET}')




