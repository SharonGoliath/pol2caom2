# pol2caom2
Application to generate a CAOM2 observation from  FITS files

# How To Run Testing

In an empty directory:

1. This is the working directory, so it should probably have some space.

1. In the master branch of this repository, find the files Dockerfile, 
docker-entrypoint.sh, and config.yml. Copy these files to the working directory.

1. Make docker-entrypoint.sh executable.

1. config.yml is configuration information for the ingestion. It will work with 
the files named and described here. For a complete description of its
content, see 
https://github.com/opencadc-metadata-curation/collection2caom2/wiki/config.yml.

1. The ways to tell this tool the work to be done:

   1. provide a file containing the list of file ids to process, one file id 
   per line, and the config.yml file containing the entries 'use_local_files' 
   set to False, and 'task_types' set to -ingest -modify. The 'todo' 
   file may provided in one of two ways:
      1. named 'todo.txt' in this directory, as specified in config.yml, or
      1. as the fully-qualified name with the --todo parameter

   1. provide the files to be processed in the working directory, and the 
   config.yml file containing the entries 'use_local_files' set to True, 
   and 'task_types' set to -store -ingest -modify.

1. To build the container image, run this:

   ```
   docker build -f Dockerfile -t pol_run ./
   ```

1. To run the application:

   ```
   user@dockerhost:<cwd># docker run --rm -ti -v <cwd>:/usr/src/app --name pol_run pol_run pol_run
   ```

1. To debug the application from inside the container:

   ```
   user@dockerhost:<cwd># docker run --rm -ti -v <cwd>:/usr/src/app --name pol_run pol_run /bin/bash
   root@53bef30d8af3:/usr/src/app# pol_run
   ```

1. To make pol2caom2 code changes visible inside the container:

   ```
   root@53bef30d8af3:/usr/src/app# pip install -e ./
   ```

1. For some instructions that might be helpful on using containers, see:
https://github.com/opencadc-metadata-curation/collection2caom2/wiki/Docker-and-Collections
