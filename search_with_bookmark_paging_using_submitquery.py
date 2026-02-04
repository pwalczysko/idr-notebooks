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

import datetime
import logging
import json
import requests
import sys
# from utils import base_url

# search url
# submit_query_url = f"{base_url}resources/submitquery/"  # noqa
# submit_query_url_new = f"https://134.36.7.77/searchengine/api/v1/resources/submitquery/"
submit_query_url_new = f"https://idr.openmicroscopy.org/searchengine/api/v1/resources/submitquery/"
submit_query_url_old = f"https://idr-testing.openmicroscopy.org/searchengine/api/v1/resources/submitquery/"
submit_query_urls = [submit_query_url_new, submit_query_url_old]
# https://134.36.7.77/searchengine/api/v1/resources/image/search/?key=Organism&value=drosophila

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def call_omero_searchengine_return_results(url, data=None, method="post"):
    if method == "post":
        resp = requests.post(url, verify=False, data=data)
    else:
        resp = requests.get(url, verify=False)
    try:
        returned_results = json.loads(resp.text)
        if not returned_results.get("results"):
            logging.info(returned_results)
            sys.exit()

        elif len(returned_results["results"]) == 0:
            logging.info("Your query returns no results")
            sys.exit()
        # get the bookmark which will be used to call
        # the next page of the results
        bookmark = returned_results["results"]["bookmark"]
        # get the size of the total results
        total_results = returned_results["results"]["size"]
        for res in returned_results["results"]["results"]:
            received_results.append(res)
            if res["id"] in ids:
                raise Exception(" Id dublicated error  %s" % res["id"])
            ids.append(res["id"])
        global total_pages
        total_pages = returned_results["results"]["total_pages"]
        return bookmark, total_results

    except Exception as ex:
        print(resp.text)
        logging.info("Error: %s" % ex)

results = []

for submit_query_url in submit_query_urls:


    received_results = []
    page = 1
    ids = []
    total_pages = 0


    """
    If the user needs to search for unhealthy human female breast images

    Clause for Human:  
    Organism='Homo sapiens' ==> {"name": "Organism", "value": "Homo sapiens", "operator": "equals","resource": "image"}  # noqa
    Restrict the search to "female":
    Sex='Female' ==> {"name": "Sex", "value": "Female", "operator": "equals","resource": "image"}  # noqa
    Restrict the search to "breast":
    Organism Part='Breast' ==>{"name": "Organism Part", "value": "Breast", "operator": "equals","resource": "image"}  # noqa
    Return only the images of "abnormal" tissues: 
    Pathology != 'Normal tissue, NOS' ==> {"name": "Pathology", "value": "Normal tissue, NOS", "operator": "not_equals","resource": "image"}  # noqa
    In terms of clauses we only have and_filters which contains 4 clauses
    """
    start = datetime.datetime.now()
    and_filters = [
        {
            "name": "Organism",
            # "value": "Homo sapiens",
            # "value": "Drosophila melanogaster",
            "value": "Danio rerio",
            "operator": "equals",
            "resource": "image",
        },
        # {
        #     "name": "Organism Part",
        #     "value": "Breast",
        #     "operator": "equals",
        #     "resource": "image",
        # },
        # {"name": "Sex", "value": "Female", "operator": "equals", "resource": "image"},
        # {
        #     "name": "Pathology",
        #     "value": "Normal tissue, NOS",
        #     "operator": "not_equals",
        #     "resource": "image",
        # },
    ]

    query_data = {"query_details": {"and_filters": and_filters}}

    query_data_json = json.dumps(query_data)
    bookmark, total_results = call_omero_searchengine_return_results(
        submit_query_url, data=query_data_json
    )

    logging.info(
        "page: %s, / %s received results: %s / %s"
        % (page, total_pages, len(received_results), total_results)
    )

    while len(received_results) < total_results:
        page += 1
        query_data_ = {"query_details": {"and_filters": and_filters}, "bookmark": bookmark}
        query_data_json_ = json.dumps(query_data_)

        next_bookmark, total_results = call_omero_searchengine_return_results(
            submit_query_url, data=query_data_json_
        )

        logging.info(
            "bookmark: %s, page: %s, / %s received results: %s / %s"
            % (bookmark, page, total_pages, len(received_results), total_results)
        )
        bookmark = next_bookmark

    # print (submit_query_url)
    results.append(received_results)

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


# for result in results:
#     print (result[0])

# print (results[0][0])

print (len(results[0]), len(results[1]))
assert len(results[0]) == len(results[1])
for i in range (0, len(results[0])):    
    added, removed, modified, same = dict_compare(results[0][i], results[1][i])
    # print(set(result[0]).intersection(result[1]))
    # print (same)
    # print (modified)
    # print (removed)
    assert len(added) == 0
    assert len(removed) == 3
    assert len(modified) == 0
