# Create minio console user
## Docker connection
docker exec -it ${MINIO_CONTAINER_NAME} /bin/bash
## Client connection
mc alias set local http://localhost:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}
### Verify login:
mc ls local

## Create console user
mc admin user add local ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY}

## Create admin policy for ${MINIO_ACCESS_KEY} user
cat > admin.json << EOF
{
	"Version": "2012-10-17",
	"Statement": [{
			"Action": [
				"admin:*"
			],
			"Effect": "Allow",
			"Sid": ""
		},
		{
			"Action": [
                "s3:*"
			],
			"Effect": "Allow",
			"Resource": [
				"arn:aws:s3:::*"
			],
			"Sid": ""
		}
	]
}
EOF

mc admin policy create local ${MINIO_ACCESS_KEY}Admin admin.json

## Set the policy for the new ${MINIO_ACCESS_KEY} user
mc admin policy attach local ${MINIO_ACCESS_KEY}Admin --user=${MINIO_ACCESS_KEY}