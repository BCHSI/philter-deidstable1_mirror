# Numbers

## Goal

Goal is to filter PHI (Protected Health Information) based numbers from clinical notes

### Rollout plan

1. Remove all numbers

2. Filter numbers and leave in numbers which are highly likely to not be PHI 

3. Build a testable and maintainable system that can be improved upon


### Known PHI

Names
Geographic data
All elements of dates
Telephone numbers
FAX numbers
Email addresses
Social Security numbers
Medical record numbers
Health plan beneficiary numbers
Account numbers
Certificate/license numbers
Vehicle identifiers and serial numbers including license plates
Device identifiers and serial numbers
Web URLs
Internet protocol addresses
Biometric identifiers (i.e. retinal scan, fingerprints)
Full face photos and comparable images
Any unique identifying number, characteristic or code


### Project Structure

1. Regex.json this holds the pattern matching regular expressions used for filtering

2. filter.py: this contains a class for useful text manipulation and actions

3. main.py: main entry point to run the program with flags and other parameters


### Regex.json Schema

A json list of regex's are maintained, these will be annotated and updated as they are improved

```
***REMOVED***
	{
		"title":"Phone number regex 001", 
		"regex":"^(\+\d{1,2}\s)?\(?\d{3}\)?***REMOVED***\s.-***REMOVED***?\d{3}***REMOVED***\s.-***REMOVED***?\d{4}$",
		"notes":"This matches the following: 
			123-456-7890
			(123) 456-7890
			123 456 7890
			123.456.7890
			+91 (123) 456-7890
			123456789"
	}, 
***REMOVED***

```