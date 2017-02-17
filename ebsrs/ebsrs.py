#!/usr/bin/env python

import argparse
import sys
import boto3
from datetime import datetime


def cleanup(old_vol_id, region):
    ec2 = boto3.client('ec2', region_name=region)

    while True:
        try:
            choice = str(input(
                'Do you want to remove the old volume? [Y/N] '
                ).lower())
        except KeyboardInterrupt:
            print('\nGoodbye!')
            sys.exit(1)
        else:
            if choice == 'y':
                print('Removing old EBS volume ({})...'
                      .format(old_vol_id))
                ec2.delete_volume(
                    VolumeId=old_vol_id
                )
                print('{} has been removed.'.format(old_vol_id))
                break
            elif choice == 'n':
                break
            else:
                print('Please choose between Y and N.')


def start_instance(ec2_id, region):
    ec2 = boto3.client('ec2', region_name=region)

    ec2.start_instances(
        InstanceIds=[
            ec2_id
        ]
    )

    waiter = ec2.get_waiter('instance_running')

    waiter.wait(
        InstanceIds=[
            ec2_id
        ]
    )

    response = ec2.describe_instances(
        InstanceIds=[
            ec2_id
        ]
    )
    instance_status = response['Reservations'][0]['Instances'][0][
                                'State']['Name']

    return instance_status


def attach_volume(new_vol_id, ec2_id, root_device, region):
    ec2 = boto3.client('ec2', region_name=region)

    ec2.attach_volume(
        VolumeId=new_vol_id,
        InstanceId=ec2_id,
        Device=root_device
    )

    waiter = ec2.get_waiter('volume_in_use')

    waiter.wait(
        VolumeIds=[
            new_vol_id
        ]
    )

    response = ec2.describe_volumes(
        VolumeIds=[
            new_vol_id
        ]
    )

    new_vol_status = response['Volumes'][0]['State']

    return new_vol_status


def detach_volume(old_vol_id, ec2_id, root_device, region):
    ec2 = boto3.client('ec2', region_name=region)

    ec2.detach_volume(
        VolumeId=old_vol_id,
        InstanceId=ec2_id,
        Device=root_device
    )

    waiter = ec2.get_waiter('volume_available')

    waiter.wait(
        VolumeIds=[
            old_vol_id
        ]
    )

    response = ec2.describe_volumes(
        VolumeIds=[
            old_vol_id
        ]
    )

    old_vol_status = response['Volumes'][0]['State']

    return old_vol_status


def stop_instance(ec2_id, region):
    ec2 = boto3.client('ec2', region_name=region)

    ec2.stop_instances(
        InstanceIds=[
            ec2_id
        ]
    )

    waiter = ec2.get_waiter('instance_stopped')

    waiter.wait(
        InstanceIds=[
            ec2_id
        ]
    )

    response = ec2.describe_instances(
        InstanceIds=[
            ec2_id
        ]
    )
    instance_status = response['Reservations'][0]['Instances'][0][
                                'State']['Name']

    return instance_status


def create_vol(snap_id, az, vol_type, iops, region):
    datetime_now = datetime.now().strftime('%Y%m%d-%H%M%S')
    ec2 = boto3.client('ec2', region_name=region)

    if vol_type == 'io1':
        cv_resp = ec2.create_volume(
            SnapshotId=snap_id,
            AvailabilityZone=az,
            VolumeType=vol_type,
            Iops=iops
        )
    else:
        cv_resp = ec2.create_volume(
            SnapshotId=snap_id,
            AvailabilityZone=az,
            VolumeType=vol_type
        )

    new_vol_id = cv_resp['VolumeId']

    waiter = ec2.get_waiter('volume_available')

    waiter.wait(
        VolumeIds=[
            new_vol_id
        ]
    )

    ec2.create_tags(
        Resources=[
            new_vol_id
        ],
        Tags=[
            {
                'Key': 'Name',
                'Value': 'restore-{0}-{1}'.format(snap_id, datetime_now)
            }
        ]
    )

    dv_resp = ec2.describe_volumes(
        VolumeIds=[
            new_vol_id
        ]
    )

    new_vol_status = dv_resp['Volumes'][0]['State']

    return new_vol_id, new_vol_status


def fetch_snapshot(vol_id, region):
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_snapshots(
        Filters=[
            {
                'Name': 'volume-id',
                'Values': [
                    vol_id
                ]
            }
        ]
    )
    snapshots = response['Snapshots']
    snap_ids = {}

    for snapshot in snapshots:
        snap_ids[snapshot['SnapshotId']] = snapshot['StartTime']

    sorted_val = [(key, snap_ids[key]) for key in sorted(snap_ids,
                  key=snap_ids.get, reverse=True)]

    return sorted_val


def fetch_root_volume(region, ec2_id):
    ec2 = boto3.client('ec2', region_name=region)
    di_resp = ec2.describe_instances(
        InstanceIds=[
            ec2_id
        ]
    )
    vol_id = di_resp['Reservations'][0]['Instances'][0][
                        'BlockDeviceMappings'][0]['Ebs']['VolumeId']
    az = di_resp['Reservations'][0]['Instances'][0][
                    'Placement']['AvailabilityZone']
    dv_resp = ec2.describe_volumes(
        VolumeIds=[
            vol_id
        ]
    )
    vol_type = dv_resp['Volumes'][0]['VolumeType']
    iops = dv_resp['Volumes'][0]['Iops']
    root_device = dv_resp['Volumes'][0]['Attachments'][0]['Device']

    return vol_id, az, vol_type, iops, root_device


def set_args():
    parser = argparse.ArgumentParser(
        description='EBS Restore Snapshot v0.1.0'
    )

    parser.add_argument(
        '-r', '--region',
        help='AWS Region',
        required=True
    )
    parser.add_argument(
        '-i',
        '--instance-id',
        help='Instance ID (i-1234567)',
        required=True
    )
    parser.add_argument(
        '-v',
        '--version',
        help='Display version',
        action='version',
        version='%(prog)s (v0.1.0)'
    )

    return parser


def main():
    parser = set_args()
    args = parser.parse_args()

    # Print help if no arguments are received
    if len(sys.argv) == 1:
        ap.print_help()
        sys.exit(1)

    region = args.region
    instance_id = args.instance_id
    count = 0
    snapshots = {}

    print('Region: {}'.format(region))
    print('InstanceId: {}'.format(instance_id))
    print('Fetching root volume of {}...'.format(instance_id))

    # Fetch root volume
    try:
        vol_id, az, vol_type, iops, root_device = fetch_root_volume(
            region, instance_id)
    except IndexError:
        print('No volume found for {}'.format(instance_id))
        sys.exit(1)

    print('VolumeId: {}'.format(vol_id))
    print('Fetching snapshots of {}...'.format(vol_id))

    # Display menu with list of available snapshots
    while True:
        for snap_id, snap_date in fetch_snapshot(vol_id, region):
            count += 1

            print('{0})\t{1}'.format(count, snap_id))
            print('\t{}\n'.format(snap_date))

            snapshots[count] = {}
            snapshots[count]['SnapshotId'] = snap_id
            snapshots[count]['SnapshotDate'] = snap_date

        try:
            if len(snapshots) == 0:
                print('No snapshots available for {}'.format(instance_id))
                sys.exit(1)
            else:
                choice = int(input('Choose a snapshot [1-{}]: '.format(count)))

                if choice < 1 or choice > count:
                    print('Please choose between 1-{}'.format(count))
                    count = 0
                else:
                    print('Your choice is [{0}] {1} - {2}'
                          .format(choice, snapshots[choice]['SnapshotId'],
                                  snapshots[choice]['SnapshotDate']))
                    break
        except KeyboardInterrupt:
            print('\nGoodbye!')
            sys.exit(1)
        except ValueError:
            print('Please choose between 1-{}'.format(count))
            count = 0

    # Create a new volume using snap_id
    print('Creating a new volume using {}...'
          .format(snapshots[choice]['SnapshotId']))

    new_vol_id, new_vol_status = create_vol(snapshots[choice]['SnapshotId'],
                                            az, vol_type, iops, region)

    if new_vol_status == 'available':
        print('NewVolumeId: {}'.format(new_vol_id))
        print('NewVolumeStatus: {}'.format(new_vol_status))

    # Stop instance
    print('Stopping {}...'.format(instance_id))

    stop_status = stop_instance(instance_id, region)

    if stop_status == 'stopped':
        print('InstanceStatus: {}'.format(stop_status))

    # Detach volume
    old_vol_id = vol_id

    print('OldVolumeId: {}'.format(old_vol_id))
    print('Detaching old volume from {}...'.format(root_device))

    old_vol_status = detach_volume(old_vol_id, instance_id,
                                   root_device, region)

    if old_vol_status == 'available':
        print('Old volume is now detached')

    # Attach volume
    print('Attaching new volume to {0} [{1}]...'
          .format(instance_id, root_device))

    attach_status = attach_volume(new_vol_id, instance_id, root_device,
                                  region)

    if attach_status == 'in-use':
        print('New volume is now attached')

    # Start instance
    print('Starting {}...'.format(instance_id))

    start_status = start_instance(instance_id, region)

    if start_status == 'running':
        print('InstanceStatus: {}'.format(start_status))

    # Cleanup
    cleanup(old_vol_id, region)

    print('Task completed successfully')
    sys.exit(0)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nGoodbye!')
        sys.exit(1)
