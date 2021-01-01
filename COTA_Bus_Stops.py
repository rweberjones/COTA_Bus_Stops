"""Purpose: This code scrapes the addresses of COTA bus stops 
in Columbus from the web and generates a CSV file of full
addresses of all COTA bus stops in Columbus."""

#import libraries + packages
from bs4 import BeautifulSoup
import requests
import csv
from geopy.geocoders import Nominatim
import array as arr

"""---------------------Declarations---------------------------"""

main_page = "https://moovitapp.com/index/en/public_transit-lines-Columbus_OH-1523-727001"
html_main_text = requests.get(main_page).text
bus_lines = BeautifulSoup(html_main_text, 'html.parser')
start_list= bus_lines.find_all("li", class_="line-item line-data mobile-line")
other_list=bus_lines.find_all("li", class_="line-item line-data collapsible")
recurse_list = []
string_list = []
website_links = []
bus_stop_locations = []

"""--------Function Defs--------"""

# MERGE_LISTS:
# function meges lists of bus lines shown on main page with
# list of bus lines after clicking "show additional lines"
def merge_lists(start_list, other_list):
    
    for elements in start_list:
        recurse_list.append(elements.find_next())
    
    for elements in other_list:
        recurse_list.append(elements.find_next())


# HAS_CHILD:
# function that checks to see if node in tree has a child
def hasChild(node):
    
    try: 
        node.children
        return True
    
    except:
        return False

# GET_WHAT_I_WANT:
# function that recursively calls itself until there is only 
# one 'a' tag remaining in each element of array            
def get_what_i_want (html_ish):
    
    for smaller in html_ish:
        if (hasChild(smaller)):
            get_what_i_want(smaller.extract())
       
# MAKE_A_STRING_LIST:
# function that takes html code from main page and pulls 
# out the "ends" of html links for each bus line
def make_a_string_list (useless_stuff):
    
    for stuff in useless_stuff:
        string_list.append(str(stuff))

# MAKE_THE_LINK:
# function that creates the html link for each bus line
def make_the_link (almost):

    for letters in almost:
        link = "https://moovitapp.com/index/en/"+letters[9:-9]
        website_links.append(link)

# GET_STOP_LOCATIONS:
# function to use list of html links and parse stop locations from
# each COTA bus line page link. Creates "Check-later" list for stops
# that do not have an address. Uses header to get stop intersection,
# then tracks the index of the previous stop that did have an address
# to use that zip code, because it is likely previous stop was also
# in same zip code
def get_stop_locations (website_links):
    
    check_later = [] #list of stops without address listed
    zip_finder=int(0) #Keep track of index of latest address that DOES exist to append index to check_later list
    
    for web_page in website_links:
        
        html_text = requests.get(web_page).text
        soup=BeautifulSoup(html_text, 'html.parser')
        stop_address=soup.find_all('span', class_="stop-address") #list of addresses of each bus stop location
        stop_name=soup.find_all('h3') #list of Bus Stop Names to keep track of in case stop address does not exist

        index = int(1) #keeps track of index match of Stop Names to Stop Addresses (Stop names start at index of 1, addresses start at index of 0)
        
        for address in stop_address:
            x=address.get_text()
            
            if len(x) > 0:
                bus_stop_locations.append(x)
                zip_finder = zip_finder + 1
            
            else:

                insert=stop_name[index] # create string of the stop name that does not have an existing address (address = " ")
                check_later.append([insert,zip_finder]) # add stop name + index of previous stop in Bus_stop_Locations to check later. Zip Code of 
                                                        # previous stop will be used in later function, as it is likely the previous 
                                                        # stop is in the same zip code as the stop lacking an address. 
                

            index = index + 1
    
    return check_later
    
# CREATE_CSV:
# fuction to open csv file stream, get full locations + zip from parsed text in 
# bus_stop_locations array, and write location data to csv file. Checks list of 
# addresses from Check_Later and uses zip codes from index of previous stop
def create_CSV (bus_stop_locations, check_later):
    
    geolocator = Nominatim(user_agent="COTA_Bus_Stops")
    outfile = open('COTA_Bus_Stop_Locations.csv','w+', newline ="")
    out_writer = csv.writer(outfile, dialect='excel')
    out_writer.writerow(['Address','Zip Code'])
    zip_codes_weird_address=[]

    for bus_stop in bus_stop_locations:
        
        if bus_stop is not None:
            
            location = geolocator.geocode(bus_stop)
            
            if location is not None:
               
                data = location.raw
                loc_data = data['display_name'].split()
                s=str(loc_data[-3])
                out_writer.writerow([location, s[:-1]])
                zip_codes_weird_address.append(s[:-1])
            
            else:
               
                out_writer.writerow([bus_stop, s[:-1]])
                zip_codes_weird_address.append(s[:-1])

    final = check_later.pop()  
    for weird_address in check_later:
        
        index_needed = weird_address[1]
        zip_code = zip_codes_weird_address[index_needed]
        out_writer.writerow([weird_address, zip_code])

    out_writer.writerow([final, zip_code])            
    outfile.close()

"""---------- Function Calls (#TELLITWHATTODO) ------------"""

merge_lists(start_list, other_list)

get_what_i_want(recurse_list)

make_a_string_list(recurse_list)

make_the_link(string_list)

check_later = get_stop_locations(website_links)

create_CSV(bus_stop_locations, check_later)
