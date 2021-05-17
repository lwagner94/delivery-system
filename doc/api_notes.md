Job service:
============
  - providers can:
    - Create jobs
    - Update jobs
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
  - Providers can:
    - Query number of agents (in proximity?)
    - Query the status/position of an agent if it currently executes a job created by this Providers
  - Agents can:
    - Set their availability (on/off duty)
    - Update their position

Route service:
==============
  - providers/Agents can:
    - Retrieve routes
    - Geocode / reverse geocode

Auth/Login service:
=============
  - Admins can:
    - create new users (email, password, role)
    - delete users
    - query all user infos

  - Everybody can:
    - Login and receive auth token
    - Fetch their own user info (e.g. to validate auth token)

  - Other services can:
    - Verify auth token and query the users role