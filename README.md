#FamilyTree Microservice

This is a Python Flask REST microservice that stores and retrieves family trees from a Postgres database.
It is set up to run in docker containers and the endpoints are exposed via NGINX.

##TODO

Need to add data access right so that users can only access records they have permissions for - most likely this will be implemented in a way that gives a person access only to records entered by that specific person.