#!/bin/bash

# Legacy alias — delegates to the full setup/run script.
exec "$(dirname "$0")/setup.sh" "$@"