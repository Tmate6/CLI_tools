# cURL to py

Generates a python script to send HTTP requests from a cURL command (given in a file).

### Arguments

- requestpath: Path to file with saved cURL command (string)
- outputpath: Path of file to output python script (string)
- requests: Number of requests to send in generated script (int)
- threads: Number of threads to use in generated script (int)
- printresponse: Print the reponse to the request (bool)
- verbose: Verbose output (bool)
