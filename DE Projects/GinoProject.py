import requests
from bs4 import BeautifulSoup as bs
import re
import ast
import pandas as pd


# initiates the response
resp = requests.get("https://www.yellowpages.com/charlotte-nc/restaurants?page=1")
soup = bs(resp.text, 'html.parser')


# gets the business name
businessName = soup.find_all('a', class_='business-name')
businessNames = []
for bn in businessName:
    bn = str(bn)
    bnVal = re.findall("<span>(.*?)<\/span>", bn)
    if len(bnVal) >= 1:
        businessNames.append(bnVal[0].replace(' &amp', ''))

#len(businessNames)

# gets the phone number and geographic data
phoneNumbers = [x.text for x in soup.find_all('div', class_='phones phone primary')]
streetAddress = [x.text for x in soup.find_all('div', class_='street-address')]
cityStateZip = [x.text for x in soup.find_all('div', class_='locality')]
cities = []
stateList = []
zipcodes = []
for c in cityStateZip:
    splitCSZ = c.split(',')
    city = splitCSZ[0]
    cities.append(city)
    state = splitCSZ[1][1:3]
    stateList.append(state)
    zipcode = splitCSZ[1][4:]
    zipcodes.append(zipcode)

# gets the reviews and counts of reviews, when applicable
ratingsDiv = soup.findAll('div', class_='ratings')
extraRatings = {}
tripAdvisorRating = {}
tripAdvisorReviewCount = {}
fourSquare = {}

for i,r in enumerate(ratingsDiv):
    tripAdvAttributeValueDict = ast.literal_eval(str(r.get('data-tripadvisor')))
    if type(tripAdvAttributeValueDict) == dict:
        tripAdvisorRating[i] = tripAdvAttributeValueDict['rating']
        tripAdvisorReviewCount[i] = tripAdvAttributeValueDict['count']
    else:
        tripAdvisorRating[i] = None
        tripAdvisorReviewCount[i] = None

    fourSquare[i] = r.get('data-foursquare')
    r = str(r)
    if 'hasExtraRating' in r:
        internalRatingValues = re.findall("(?<=result-rating)(\s*\w*\s*\w*)\"", r)
        extraRatings[i] = internalRatingValues[0][1:]
    else:
        extraRatings[i] = None

internalRatingCounts = [x.text.replace('(', '').replace(')', '') for x in soup.find_all('span', class_='count')]

# gets the all of these values below
main = soup.findAll('div', class_='search-results organic')
yearsBiz = {}
firstReviewText = {}
websiteDict = {}
menuDict = {}
priceRangeDict = {}
for m in main:
    t = m.find_all("div", {"class": "result"})
    for i,s in enumerate(t):
        if 'Website' in str(s):
            websiteDict[i] = s.find('a', 'track-visit-website').get("href")
        else:
            websiteDict[i] = None
        if '"listing_features":"menu-link"' in str(s):
            menuDict[i] = "www.yellowpages.com" + s.find('a', 'menu').get('href')
        else:
            menuDict[i] = None
        if '"listing_features":"menu-link"' in str(s):
            menuDict[i] = "www.yellowpages.com" + s.find('a', 'menu').get('href')
        else:
            menuDict[i] = None
        if 'number' in str(s):
            yearsBiz[i] = s.find('div', 'number').text
        else:
            yearsBiz[i] = None
        if 'body with-avatar' in str(s):
            firstReviewText[i] = s.find('p', 'body with-avatar').text
        else:
            firstReviewText[i] = None
        if 'price-range' in str(s):
            priceRangeDict[i] = s.find('div', 'price-range').text
        else:
            priceRangeDict[i] = None



restaurantsOnPage = {}
for i,e in enumerate(phoneNumbers):
    restaurantsOnPage[e] = [
    businessNames[i],
    phoneNumbers[i],
    streetAddress[i],
    cities[i],
    stateList[i],
    zipcodes[i],
    websiteDict[i],
    menuDict[i],
    yearsBiz[i],
    firstReviewText[i],
    extraRatings[i],
    internalRatingCounts[i],
    tripAdvisorRating[i],
    tripAdvisorReviewCount[i],
    fourSquare[i],
    priceRangeDict[i]
]


df = pd.DataFrame.from_dict(restaurantsOnPage).transpose().reset_index()
df.columns = ['primaryKey', 'businessName', 'phoneNumber', 'streetAddress', 'city', 'state', 'zipCode', 'website', 'menu', 'yearsInBusiness', 'firstReviewText', 'internalRating', 'internalRatingsCount',
              'tripAdvisorRating', 'tripAdvisorReviewCounts', 'fourSquareRating', 'priceRange']
print(df)



