# About

[![forthebadge](http://forthebadge.com/images/badges/built-with-love.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/powered-by-oxygen.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/fuck-it-ship-it.svg)](http://forthebadge.com)

A Python script that can restore snapshots created by [ebs-snapshot-python](https://github.com/jpdoria/ebs-snapshot-python).

# Prerequisite

You can configure your account on your local machine using `aws configure`.

If you want to use this on EC2, make sure the instance has a role (best practice).

This is the IAM policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt0123456789012",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeVolumes",
                "ec2:DescribeSnapshots",
                "ec2:CreateVolume",
                "ec2:CreateTags",
                "ec2:StopInstances",
                "ec2:DetachVolume",
                "ec2:AttachVolume",
                "ec2:StartInstances"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```

# Usage

```bash
# ./ebs-restore-snapshot.py
usage: ebs-restore-snapshot.py [-h] -r REGION -i INSTANCE_ID
ebs-restore-snapshot.py: error: the following arguments are required: -r/--region, -i/--instance-id
# ./ebs-restore-snapshot.py --help
usage: ebs-restore-snapshot.py [-h] -r REGION -i INSTANCE_ID

EBS Restore Snapshot v1.0

optional arguments:
  -h, --help            show this help message and exit
  -r REGION, --region REGION
                        AWS Region
  -i INSTANCE_ID, --instance-id INSTANCE_ID
                        Instance ID (i-1234567)
#
```

# Example

```bash
# ./ebs-restore-snapshot.py --region ap-southeast-1 --instance-id i-9652b917
2016-Dec-23 02:54:37 PM | INFO - main - Region: ap-southeast-1
2016-Dec-23 02:54:37 PM | INFO - main - InstanceId: i-9652b917
2016-Dec-23 02:54:37 PM | INFO - main - Fetching root volume of i-9652b917...
2016-Dec-23 02:54:37 PM | INFO - load - Found credentials in shared credentials file: ~/.aws/credentials
2016-Dec-23 02:54:38 PM | INFO - _new_conn - Starting new HTTPS connection (1): ec2.ap-southeast-1.amazonaws.com
2016-Dec-23 02:54:40 PM | INFO - main - VolumeId: vol-817b0e05
2016-Dec-23 02:54:40 PM | INFO - main - Fetching snapshots of vol-817b0e05...
2016-Dec-23 02:54:40 PM | INFO - _new_conn - Starting new HTTPS connection (1): ec2.ap-southeast-1.amazonaws.com
1)	snap-0bff7c87332e5b6e8
	2016-12-23 04:18:54+00:00

2)	snap-03a9ab12b8d6df2a2
	2016-12-22 04:18:51+00:00

3)	snap-0599e851d5cb48ba6
	2016-12-21 04:18:52+00:00

Choose a snapshot [1-3]: 3
2016-Dec-23 02:54:46 PM | INFO - main - Your choice is [3] snap-0599e851d5cb48ba6 - 2016-12-21 04:18:52+00:00
2016-Dec-23 02:54:46 PM | INFO - main - Creating a new volume using snap-0599e851d5cb48ba6...
2016-Dec-23 02:54:46 PM | INFO - _new_conn - Starting new HTTPS connection (1): ec2.ap-southeast-1.amazonaws.com
2016-Dec-23 02:55:03 PM | INFO - _get_conn - Resetting dropped connection: ec2.ap-southeast-1.amazonaws.com
2016-Dec-23 02:55:05 PM | INFO - main - NewVolumeId: vol-07870a991d3510f3d
2016-Dec-23 02:55:05 PM | INFO - main - NewVolumeStatus: available
2016-Dec-23 02:55:05 PM | INFO - main - Stopping i-9652b917...
2016-Dec-23 02:55:05 PM | INFO - _new_conn - Starting new HTTPS connection (1): ec2.ap-southeast-1.amazonaws.com
2016-Dec-23 02:55:22 PM | INFO - _get_conn - Resetting dropped connection: ec2.ap-southeast-1.amazonaws.com
2016-Dec-23 02:55:39 PM | INFO - _get_conn - Resetting dropped connection: ec2.ap-southeast-1.amazonaws.com
2016-Dec-23 02:55:42 PM | INFO - main - InstanceStatus: stopped
2016-Dec-23 02:55:42 PM | INFO - main - OldVolumeId: vol-817b0e05
2016-Dec-23 02:55:42 PM | INFO - main - Detaching old volume from /dev/xvda...
2016-Dec-23 02:55:42 PM | INFO - _new_conn - Starting new HTTPS connection (1): ec2.ap-southeast-1.amazonaws.com
2016-Dec-23 02:55:59 PM | INFO - _get_conn - Resetting dropped connection: ec2.ap-southeast-1.amazonaws.com
2016-Dec-23 02:56:01 PM | INFO - main - Old volume is now detached
2016-Dec-23 02:56:01 PM | INFO - main - Attaching new volume to i-9652b917 [/dev/xvda]...
2016-Dec-23 02:56:01 PM | INFO - _new_conn - Starting new HTTPS connection (1): ec2.ap-southeast-1.amazonaws.com
2016-Dec-23 02:56:03 PM | INFO - main - New volume is now attached
2016-Dec-23 02:56:03 PM | INFO - main - Starting i-9652b917...
2016-Dec-23 02:56:03 PM | INFO - _new_conn - Starting new HTTPS connection (1): ec2.ap-southeast-1.amazonaws.com
2016-Dec-23 02:56:20 PM | INFO - _get_conn - Resetting dropped connection: ec2.ap-southeast-1.amazonaws.com
2016-Dec-23 02:56:22 PM | INFO - main - InstanceStatus: running
2016-Dec-23 02:56:22 PM | INFO - main - Task completed successfully
#
```

# Contribution

This project is still young and there are things that need to be done. If you have ideas that would improve this app, feel free to contribute!

# License

MIT License

Copyright (c) 2017 John Paul P. Doria

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.