Job service:
============
  - Customers can:
    - Create jobs
    - Update jobs
    - Delete jobs
    - Query job status
    - Retrieve a list of their jobs
  - Agents can:
    - Query jobs in a given radius
    - Claim jobs
    - Cancel the claim
    - Set status: picked up/delivered, ETA
  - End users can:
    - Query the status of a job (ETA, picked up, delivered)
  
Agent service:
=============
  - Customers can:
    - Query number of agents (in proximity?)
    - Query the status/position of an agent if it currently executes a job created by this customer
  - Agents can:
    - Set their availability (on/off duty)
    - Update their position

Route service:
==============
  - Customers/Agents can:
    - Retrieve routes
    - Geocode / reverse geocode

Auth/Login service:
=============
  - Admins can:
    - create Customers
    - delete Customers
    - create Agents
    - delete Agents

  - Everybody can:
    - Login and receive auth token

  - Other services can:
    - Verify auth token and query the users role
    
  