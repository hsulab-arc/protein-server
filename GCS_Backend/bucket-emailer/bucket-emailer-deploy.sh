#!/bin/bash

gcloud functions deploy protein-server-userdata-file-listener \
--gen2 \
--runtime=python311 \
--region=us-west1 \
--source=./GCS_Backend/bucket-emailer/ \
--entry-point=main \
--trigger-location=us-west1 \
--env-vars-file=./GCS_Backend/bucket-emailer/bucket-emailer-env.yaml \
--trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
--trigger-event-filters="bucket=protein-server-userdata"