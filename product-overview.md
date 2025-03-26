# Cratr

## Goals
Cratr is a tool for locating meteorites containing specific materials. NASA's open data provides us with the locations and composition classifications of all known meteorite falls, users who need minerals and elements that would be otherwise hard to locate can use Cratr to easily find the locally sourced materials they need.

## MVP Features

- **Mapping of meteorite classifications to compositional materials**: Meteorite classifications are based on many factors aside from just composition, Cratr will simplify these classifications into well-known materials.
- **Regular updates**: The NASA open data API allows Cratr to check regularly for new or changed meteorite data and update the database accordingly.
- **Map based search**: Cratr will provide a map for users to locate meteorites within a given radius of their location and filters to specify which materials to search. The Map will be populated with markers using our simplified classifications.

## Additional Features
- **Reverse geolocation**: Allow users to type a location instead of using current GPS coordinates, find that location on the map and perform the search there.
- **Rank results**: Use the materials as a percentage of the mass (in grams) for each meteorite found to weight likely locations of search materials and display them to the user in ranked order.
- **Link to actual meteorites for sale**: Link to meteoritemarket or similar for the given class/specific name; matching to any specific listings is going to be difficult with varying naming schemes.
- **Notifications**: Allow users to subscribe to emails notifying when new meteorites matching their given material criteria are added to the list.