#!/bin/bash
set -e

# Define a timestamp function
timestamp() {
  date +"%Y%m%d%H%M%S"
}

# Get bucket name, note and job name
bucket_name=$1
note=$2
job_name=esmfold-inference-$(timestamp)$note
echo "Bucket name: ${bucket_name}"
echo "Job name: ${job_name}"

# Use sed to replace the job name placeholder with the unique job name, 
# and the bucket name placeholder with the unique bucket name
# for MacOS, sed -i requires you to set a backup file, so a backup job.yaml.backup is created
sed "s/job-name-placeholder/$job_name/g" ./esmfold_template.yaml > job.yaml
sed -i.backup "s#bucket-name-placeholder#$bucket_name#g" job.yaml

# Apply the job configuration
kubectl apply -f job.yaml

# Optionally, remove the generated job.yaml after running the job
# rm job.yaml
