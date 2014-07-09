# Copyright 2014 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This set of functions define the interactions with the catkin_tools metadata
# file, `.catkin_tools.yml`. This file can be used by each verb to store
# verb-specific information 

from __future__ import print_function

import os
import shutil
import yaml

METADATA_DIR_NAME = '.catkin_tools'

METADATA_README_TEXT = """\
# Catkin Tools Metadata

This directory was generated by catkin_tools and it contains persistent
configuration information used by the `catkin` command and its sub-commands.

Please see the catkin_tools documentation before editing any files in this
directory.
"""

def get_paths(workspace_path, verb=None):
    """Get the path to a metadata directory and verb-specific metadata file.

    :workspace_path: The path to the root of a catkin workspace
    :verb: (optional) The catkin_tools verb with which this information is associated.

    :returns: A tuple of the metadata directory and the verb-specific file path, if given
    """

    metadata_dir = os.path.join(workspace_path, METADATA_DIR_NAME)
    metadata_file_path = os.path.join(metadata_dir, '%s.yml' % verb) if verb else None

    return (metadata_dir, metadata_file_path)


def find_enclosing_workspace(search_start_path):
    """Find a catkin workspace based on the existence of a catkin_tools
    metadata directory starting in the path given by search_path and traversing
    each parent directory until either finding such a directory or getting to
    the root of the filesystem.
    
    :search_start_path: Directory which either is a catkin workspace or is
    contained in a catkin workspace

    :returns: Path to the workspace if found, `None` if not found.
    """
    while True:
        # Check if marker file exists
        (candidate_path, _) = get_paths(search_start_path)
        if os.path.exists(candidate_path) and os.path.isdir(candidate_path):
            return search_start_path 

        # Update search path or end
        (search_start_path, child_dir) = os.path.split(search_start_path)
        if len(child_dir) == 0:
            break

    return None

def init_metadata_dir(workspace_path, reset=False):
    """Create or reset a catkin_tools metadata directory with no content in a given path.

    :workspace_path: The path to the root of a catkin workspace
    :reset: If true, clear the metadata directory of all information 
    """
    
    # Make sure the directory
    if not os.path.exists(workspace_path):
        raise IOError("Can't initialize Catkin workspace in path %s "
            "because it does not exist." % (workspace_path))

    # Check if the desired workspace is enclosed in another workspace
    marked_workspace = find_enclosing_workspace(workspace_path)

    if marked_workspace and marked_workspace != workspace_path:
        raise IOError("Can't initialize Catkin workspace in path %s "
            "because it is already contained in another workspace: %s." %
            (workspace_path, marked_workspace))
        
    # Construct the full path to the metadata directory
    (metadata_dir, _) = get_paths(workspace_path)

    # Check if a metadata file already exists
    if os.path.exists(metadata_dir):
        # Reset the directory if requested
        if reset:
            print("Deleting existing metadata from catkin_tools metadata directory: %s" % (metadata_dir))
            shutil.rmtree(metadata_dir)
            os.mkdir(metadata_dir)
    else:
        # Create a new .catkin_tools directory
        os.mkdir(metadata_dir)

    # Write the README file describing the directory
    with open(os.path.join(metadata_dir,'README'),'w') as metadata_readme:
        metadata_readme.write(METADATA_README_TEXT)

def get_metadata(workspace_path, verb):
    """Get a python structure representing the metadata for a given verb.

    :workspace_path: The path to the root of a catkin workspace
    :verb: The catkin_tools verb with which this information is associated

    :returns: A python structure representing the YAML file contents (empty
    dict if the file does not exist)
    """

    (metadata_dir, metadata_file_path) = get_paths(workspace_path, verb)

    if not os.path.exists(metadata_file_path):
        return {}

    with open(metadata_file_path,'r') as metadata_file:
        return yaml.load(metadata_file)

def update_metadata(workspace_path, verb, new_data = {}):
    """Update the catkin_tools metadata file corresponding to a given verb.

    :workspace_path: The path to the root of a catkin workspace
    :verb: The catkin_tools verb with which this information is associated
    :new_data: A python dictionary or array to write to the metadata file
    """

    (metadata_dir, metadata_file_path) = get_paths(workspace_path, verb)

    # Make sure the metadata directory exists
    init_metadata_dir(workspace_path)

    # Get the curent metadata for this verb
    data = get_metadata(metadata_dir, verb) or dict()

    # Update the metadata for this verb
    data.update(new_data)
    with open(metadata_file_path,'w') as metadata_file:
        yaml.dump(data, metadata_file, default_flow_style=False)
