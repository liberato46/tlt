import boto3

def upload_s3(voice_url, file_id):
	filename=file_id+".ogg"
	client=boto3.client("s3")
	client.upload_file(voice_url, "tltbot", filename)
	bucket_location = client.get_bucket_location(Bucket='tltbot')
	return "https://s3-{0}.amazonaws.com/{1}/{2}".format(
       bucket_location['LocationConstraint'],
       'tltbot',
       filename)