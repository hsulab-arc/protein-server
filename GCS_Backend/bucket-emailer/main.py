from cloudevents.http import CloudEvent
import functions_framework
import base64
import os
from google.cloud import storage, error_reporting
import sendgrid
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileType, FileName, Disposition

error_client = error_reporting.Client()

def notify_via_email(data):
    print("Sending email")
    # Configure SendGrid
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))

    # Get the file information
    file_name = data['name']
    file_name_truncated = file_name.split('/')[-1]
    bucket_name = data['bucket']
    time_created = data['timeCreated']

    # Create a client
    project = os.environ.get('GCP_PROJECT')
    bucket = os.environ.get('GCS_BUCKET')
    try:
        storage_client = storage.Client(project=project)
        print(storage_client.list_buckets())

        # Download the file into bytes to send in the email
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.get_blob(file_name)
        file_bytes = blob.download_as_bytes()
    except RuntimeError as e:
        error_client.report_exception()
        print(f"Error while working with GCS client: {e}")
        pass

    try:
        # Compose the email
        message = Mail(
            from_email='matthewn@arcinstitute.org',
            to_emails='matthewn@arcinstitute.org',
            subject=f'New file created in GCS',
            html_content=f'<strong>A new file named {file_name} was created in bucket {bucket_name} at {time_created}. The file is attached to this email. </strong>')
        
        # Generate the attachment
        encoded = base64.b64encode(file_bytes).decode()
        attachment = Attachment()
        attachment.file_content = FileContent(encoded)
        attachment.file_type = FileType('text/plain')
        attachment.file_name = FileName(file_name_truncated)
        attachment.disposition = Disposition('attachment')
        message.attachment = attachment


        # Send the email
        response = sg.send(message)
    except RuntimeError as e:
        error_client.report_exception()
        print(f"Error while sending email: {e}")
        pass

    return response



def handle_fasta(data):
    # Email the user of the uploaded file
    notify_via_email(data)

    # Create a new K8 ESM job


def handle_data(data):
    # Email the user of the uploaded file
    notify_via_email(data)

    # Return the data to the frontend

# Triggered by a change in a storage bucket
# [TO-DO] grab user email from GCP
@functions_framework.cloud_event
def main(cloud_event: CloudEvent) -> tuple:
    """This function is triggered by a change in a storage bucket.

    Args:
        cloud_event: The CloudEvent that triggered this function.
    Returns:
        The event ID, event type, bucket, name, metageneration, and timeCreated.
    """
    data = cloud_event.data

    event_id = cloud_event["id"]
    event_type = cloud_event["type"]

    bucket = data["bucket"]
    name = data["name"]
    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]

    filetype = name.split(".")[-1]

    ## If the uploaded file is a fasta, then it has come from the user. Create a new K8 ESM job, and send an email.
    if filetype == "fasta":
        handle_fasta(data)

    ## If the uploaded file is a pdb or csv file, then it has come from the K8 ESM job. Send an email.
    elif filetype == "csv" or filetype == "pdb":
        handle_data(data)

    else:
        print("Unhandled file type. File types must be fasta, csv, or pdb.")

    
    print(f"Event ID: {event_id}")
    print(f"Event type: {event_type}")
    print(f"Bucket: {bucket}")
    print(f"File: {name}")
    print(f"Metageneration: {metageneration}")
    print(f"Created: {timeCreated}")
    print(f"Updated: {updated}")

    return event_id, event_type, bucket, name, metageneration, timeCreated, updated
