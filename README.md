# CiscoEOLCheck
Checks EOL of serials submitted via CSV against the online API

## Get EOL Dates from Cisco Support API
1. clone the git repo by navigating to where you want the files to be in your local filesystem and run the following command

```
git clone https://github.com/lheavrin/CiscoEOLCheck.git
cd CiscoEOLCheck
```
2. Create a virtual environment using the requirements.txt that was part of the git clone

```python3 -m venv env
source env/bin/activate
```

Your prompt should now look like this

```
(env) computername$
```

3. Download all the packages from requirements.txt within your virtual environment.  This will take a little while

```
pip install -r requirements.txt
```

4. Collect a CSV of serial numbers, 1 per row in excel and save it in the CiscoEOLCheck folder, where you should currently be.  The filename should be eolserials.csv, though it is not mandatory.

5. You are now ready to run the EOL API call using Python.  When prompted, enter your API credentials from https://apiconsole.cisco.com and the filename of the serials you collected (or press enter for eolserials.csv).

```
python ciscoEOL.py 
```

Example:
```
(env) lynns-mbp-m1$ python ciscoEOL.py
==================================================
Please enter your Cisco Support Client ID: abc123456
Please enter your Cisco Support Client Secret:
==================================================
Please choose file [eolserials.csv]:
Progress: [ 20 / 9725 ]
   deviceserial     EOLDate
0   FCW2212NFRH  2027-10-31
1   FCW2212NFQL  2027-10-31
2   FCW2212NFR4  2027-10-31
3   FCW2212NE8A  2027-10-31
4   FGL2224B2VK  2027-04-30
5   FGL2224B2WK  2027-04-30
```
The report will run and will take around 15 minutes.
When the report is complete there will be a file named eolreport.csv in the same directory you are in
