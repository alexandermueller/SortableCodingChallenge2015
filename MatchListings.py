#!/usr/bin/python

# Sortable Coding Challenge - Alexander Mueller

import json, io, os.path

listingsFilePath = './InputData/listings.txt'
productsFilePath = './InputData/products.txt'
resultsFilePath = './ResultingData/results.txt'

filesMissing = []
if not os.path.isfile(listingsFilePath):
    filesMissing.insert(0, listingsFilePath)
if not os.path.isfile(productsFilePath):
    filesMissing.insert(0, productsFilePath)

if len(filesMissing) > 0:
    print "Error! The following files are missing:"
    for fileMissing in filesMissing:
        print fileMissing
else:
    listingsFile = open(listingsFilePath, 'r')
    productsFile = open(productsFilePath, 'r')
    resultsFile = io.open(resultsFilePath, 'w+', encoding='utf8')   # Need to preserve the encodings of all the listings

    products = {}
    matches = {}

    # Create product listing dictionary
    # Products are sorted in the dictionary in order of: manufacturer->family->model
    # Products that have no family listing are placed in order of: manufacturer->model

    for line in productsFile:
        product = json.loads(line)
        manufacturer = product['manufacturer'].lower()
        family = ''
        model = product['model'].lower()

        if manufacturer not in products:
            products[manufacturer] = {}
        
        if 'family' in product:
            family = product['family'].lower()
            if family not in products[manufacturer]:
                products[manufacturer][family] = {}
            
            if model not in products[manufacturer][family]:
                products[manufacturer][family][model] = { 'product_name' : product['product_name'] }
        elif model not in products[manufacturer]:
                products[manufacturer][model] = { 'product_name' : product['product_name'] }


    # Iterate through file of listings.

    counter = 0 # Used to record all the matches made for stats purposes
    distribution = {}
    for line in listingsFile:
        listing = json.loads(line)
        if 'title' in listing:                                                                                                  
            title = ''.join([ char if char.isalnum() or char.isspace() or char == '-' else '' for char in listing['title'] ])   # Remove all chars in the listing that aren't Alphanumberic, Whitespace, or -
            title = ' '.join(title.split('  ')).lower()                                                                         # Remove the leftover extra Whitespace characters to have proper spacing again
            wordList = []

            # All manufacturers in the products json file have one word names, split names for listings that have more than one word in them
            if not listing['manufacturer'] == '':
                wordList = listing['manufacturer'].lower().split(' ')   
            
            # Save the manufacturer name that exists as a key in the products dict
            manufacturer = ''
            for word in wordList:
                if word in products:                        
                    manufacturer = word
                    break

            # If a manufacturer name was found, then search through the listing title for matching product names
            if not manufacturer == '':
                wordList = title.split(' ')
                nextCategory = ''
                currentLevel = products[manufacturer]
                accessoryLocation = len(wordList)                                                                               
                for i in xrange(len(wordList)):                                                                                
                    word = wordList[i]
                    # Remember wherever the word 'for' pops up. If 'for' is in front of the first occurence of a proper product name, then it is most likely an accessory
                    if word == 'for':
                        accessoryLocation = i
                    elif word in currentLevel and i < accessoryLocation:
                        nextCategory = word
                        currentLevel = currentLevel[nextCategory]
                    elif i < (len(wordList) - 1) and (word + " " + wordList[i + 1]) in currentLevel and i < accessoryLocation:
                        nextCategory = word + " " + wordList[i + 1]
                        currentLevel = currentLevel[nextCategory]

                    # The listing title contains a valid product if we've progressed through the dictionary to a level that contains a product listing
                    if 'product_name' in currentLevel:
                        name = currentLevel['product_name']
                        
                        # Record the listing that matched a product in the product dictionary into the matches dictionary
                        if name not in matches:
                            matches[name] = { "product_name" : name, "listings" : [listing] }
                        else: 
                            matches[name]["listings"].insert(0, listing)
                        counter += 1
                        break

    # We've finished matching the listings with products, now we just need to write the required JSON to the results file
    for key in matches.keys(): # Each key is a unique product name
        jsonData = json.dumps(matches[key], ensure_ascii=False) + '\n'
        resultsFile.write(jsonData)
    resultsFile.close()
    print "Found %d total matches for %d unique products." % (counter,len(matches.keys()))