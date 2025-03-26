# Cratr Technical

## Overview
 ![System overview diagram](system.svg)

## Backend Services
- ~~Fly.io~~
	- Essentially just running a VM constantly
	- Lots more overhead on building API server
	- Lose db if it restarts
- AWS 
	- Only runs backend when needed
	- API Gateway to trigger Lambda & S3 static hosting is easy
### Classifier 
Python tool for ingesting the NASA meteorite data and matching the classifications to our known/simplified schema.

- Uses fuzzy string matching and removes some generic terms from `recclass` field to match expected classifications
- Validates required fields such as location and normalizes different formats of lat/lng
- Outputs a list of cleaned meteorite data ready to store in the database

### Updater
Python tool to fetch new NASA data, classify it, and store it in the database

- Runs in AWS Lambda on demand (cron)
- Makes API requests to fetch all NASA open data within limits (paginated at 5000 max)
- Run data through Classifier 
- Find ids not yet present in database, add classified rows

### Database 
~~DynamoDB storage for meteorite objects~~

- Difficult to check for existing meteorite ids and whether fields have changed
- Can't directly query for locations within radius (https://aws.amazon.com/blogs/mobile/geo-library-for-amazon-dynamodb-part-1-table-structure/ geohashing adds a lot of complexity when MySQL can do this natively)

MySQL storage for meteorite data

- Use ~~Haversine formula~~ (ST_Distance_Sphere builtin function) in query to find rows within a radius of a given location
- Use NASA data ids as primary key, enforce uniqueness constraint and check for known/new meteorites

### API
Python backend to provide data to the frontend

- Run in AWS Lambda
- Build DB location query based on queryparams: lat, long, radius

## Frontend
User facing website to geolocate the user, make an API request, display results as markers on a map

- Static hosting in S3 bucket, public access via CloudFront domain
- React/Vite for quick scaffolding and prototype
	- Typescript, Tailwind CSS
	- Leaflet library for OpenStreetMaps

## Other Dependencies

### Classifier Schema
Manually created mapping for Classifier and Frontend to use. See https://www.meteoritemarket.com/type.htm, and https://www.lpi.usra.edu/meteor/metbullclass.php?sea for details.

Example:

````
[
  {
    "classifiers": ["Enstatite", "enst", "E3", "E4", "E5", "E6", "E7"],
    "name": "Enstatite Chondrite",
    "resources": ["iron", "enstatite", "troilite", "plagioclase", "olivine"],
    "id": "E"
  },
  ...
]
````

- **classifiers**: list of any class definitions that should fall into this classification, combining classes with different alteration details (numeric designation) to simplify differences irrelevant to us. Used to fuzzy string match, should include full titles and any abbreviations or other formats.
- **name**: display name for this class
- **resources**: list of the most basic mineral/element resources that are present in meteorites of this class
- **id**: internal unique classification id

## Future improvements

### Updater optimization
Updater fetches all NASA data and classifies it before checking for known ids in the database. This is because the Classifier simply ignores invalid rows, so to compare lists we have to complete that filtering first. We should instead track *all* ids in the database, marking invalid rows as such with a boolean field. Then we can check ids returned in the API set for unknown ones before running the Classifier, exiting early if no changes are found.

### Caching
- The frontend makes a new API request whenever the map changes, it should limit requests to only new areas and reuse past results when possible.

- The backend will run a query for every request, we can likely cache results for large areas and return the same result set for queries within them.

### Local Testing
Use docker-compose to run a local instance of MySQL and API wrappers to approximate AWS services which can be used for local/integration testing

### Continuous Deployment
Deploy tasks are run locally with scripts to push to AWS, use GitHub actions to run tests and deploy automatically on commit