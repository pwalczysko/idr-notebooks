#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2022 University of Dundee & Open Microscopy Environment.
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import requests
import json
import sys
# from utils import base_url

# url to send the query
image_value_search = "/resources/image/searchvalues/"
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# Get the available attributes for a resource, e.g. image
image_attributes = "/resources/image/keys/"
# Get available values for a resource attribute
image_key_values = "resources/image/searchvaluesusingkey/"
base_url_old = "https://idr-testing.openmicroscopy.org/searchengine/api/v1/"
base_url = "https://134.36.7.77/searchengine/api/v1/"

base_urls = [base_url_old, base_url]

results = []

for base_url in base_urls:

    received_results = []

    """
    In case the user needs to know the available attributes for images
    """
    attrs_url = "{base_url}{image_attributes}".format(
        image_attributes=image_attributes, base_url=base_url
    )

    resp = requests.get(url=attrs_url, verify=False)
    ress = json.loads(resp.text)
    # a list containing the available attributes
    for res in ress:
        data_source = res.get("data_source")
        if not data_source:
            continue
        print("Checking data source: %s " % data_source)
        attributes = res.get("image")
        logging.info(
            "Number of available attributes for images: %s" % len(attributes)
        )  # noqa

        """
        The user can get the available values for the "Organism" attribute
        and the number of images for each value
        """
        # key = "Organism"
        key = "Protein"
        values_attr_url = (
            "{base_url}{image_key_values}?key={key}&data_source={data_source}".format(
                base_url=base_url,
                image_key_values=image_key_values,
                key=key,
                data_source=data_source,
            )
        )
        print(values_attr_url)
        resp = requests.get(url=values_attr_url, verify=False)
        res = json.loads(resp.text)
        # a list containing dicts of the available values with the number of images
        buckets = res.get("data")
        logging.info(
            "Number of available buckets for attribute %s is %s" % (key, len(buckets))
        )
        # The first bucket
        for bucket in buckets:
            logging.info("Bucket details: %s " % bucket)
    results.append(buckets)
print (results)

def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    # print(d1_keys)
    # print(d2_keys)
    shared_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys  
    # print (shared_keys)
    # for o in shared_keys:
    #     print (d1[o])
    # print (added)
    # modified = {o : (d1[o], d2[o]) for o in shared_keys if d1[o].sort() != d2[o].sort()}
    modified = {o : (d1[o], d2[o]) for o in shared_keys if d1[o] != d2[o]}
    # same = set(o for o in shared_keys if d1[o].sort() == d2[o].sort())
    same = set(o for o in shared_keys if d1[o] == d2[o])
    return added, removed, modified, same

# print (results[0][0]['key_values'][0]['value'])
print (len(results[0]), len(results[1]))
assert len(results[0]) == len(results[1])
for i in range (0, len(results[0])):    
    added, removed, modified, same = dict_compare(results[0][i], results[1][i])
    # print(set(result[0]).intersection(result[1]))
    # print (same)
    # print (modified)
    # print (removed)
    assert len(added) == 0
    assert len(removed) == 0
    assert len(modified) == 0
    # print (i, "comparing")