# About

Restore snapshots created by [ebs-snapshot-python](https://github.com/jpdoria/ebs-snapshot-python).

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

# Installation

```bash
pip install ebsrs
```

# Usage

```bash
# ebsrs
usage: ebsrs [-h] -r REGION -i INSTANCE_ID [-v]
ebsrs: error: the following arguments are required: -r/--region, -i/--instance-id
# ebsrs --help
usage: ebsrs [-h] -r REGION -i INSTANCE_ID [-v]

EBS Restore Snapshot v0.1.0

optional arguments:
  -h, --help            show this help message and exit
  -r REGION, --region REGION
                        AWS Region
  -i INSTANCE_ID, --instance-id INSTANCE_ID
                        Instance ID (i-1234567)
  -v, --version         Display version
#
```

# Example

```bash
# ebsrs -r ap-southeast-1 -i i-2f0b2aa1
Region: ap-southeast-1
InstanceId: i-2f0b2aa1
Fetching root volume of i-2f0b2aa1...
VolumeId: vol-0fd09c171ebdac8f5
Fetching snapshots of vol-0fd09c171ebdac8f5...
1)	snap-06591742121affdac
	2017-02-16 16:01:08+00:00

2)	snap-01973940c534a685f
	2017-02-15 16:01:09+00:00

3)	snap-04459a725001860b7
	2017-02-14 16:01:09+00:00

Choose a snapshot [1-3]: 3
Your choice is [3] snap-04459a725001860b7 - 2017-02-14 16:01:09+00:00
Creating a new volume using snap-04459a725001860b7...
NewVolumeId: vol-07e5a167e70b6f036
NewVolumeStatus: available
Stopping i-2f0b2aa1...
InstanceStatus: stopped
OldVolumeId: vol-0fd09c171ebdac8f5
Detaching old volume from /dev/sda1...
Old volume is now detached
Attaching new volume to i-2f0b2aa1 [/dev/sda1]...
New volume is now attached
Starting i-2f0b2aa1...
InstanceStatus: running
Do you want to remove the old volume? [Y/N] y
Removing old EBS volume (vol-0fd09c171ebdac8f5)...
vol-0fd09c171ebdac8f5 has been removed.
Task completed successfully
#
```

# Contributing

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