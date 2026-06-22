# Volumes and Bind Mounts

## Overview
- Generally Docker Containers are ephimeral
- Data Loss : Any data written to the container's internal writable layer disappears when the container stops or is deleted.
- Immutability: They are not meant to be manually patched or updated while running. Instead, you deploy an entirely new container from an updated image

# Bind Mounts:
