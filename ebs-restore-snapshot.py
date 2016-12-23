#!/usr/bin/env python3

import argparse
import logging
import sys
import boto3
from datetime import datetime


def start_instance(ec2_id):
    try:
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
        instance_status = response['Reservations'][0]['Instances'][0]['State']['Name']

        return instance_status
    except Exception as e:
        logger.error(e, exc_info=True)
        sys.exit(1)


def attach_volume(new_vol_id, ec2_id, root_device):
    try:
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
    except:
        raise


def detach_volume(old_vol_id, ec2_id, root_device):
    try:
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
    except Exception as e:
        logger.error(e, exc_info=True)
        sys.exit(1)


def stop_instance(ec2_id):
    try:
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
        instance_status = response['Reservations'][0]['Instances'][0]['State']['Name']

        return instance_status
    except Exception as e:
        logger.error(e, exc_info=True)
        sys.exit(1)


def create_vol(snap_id, az, vol_type, iops):
    try:
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
    except Exception as e:
        logger.error(e, exc_info=True)
        sys.exit(1)


def fetch_snapshot(vol_id):
    try:
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

        sorted_val = [(key, snap_ids[key]) for key in sorted(snap_ids, key=snap_ids.get, reverse=True)]

        return sorted_val
    except Exception as e:
        logger.error(e, exc_info=True)
        sys.exit(1)


def fetch_root_volume():
    try:
        ec2 = boto3.client('ec2', region_name=region)
        di_resp = ec2.describe_instances(
            InstanceIds=[
                instance_id
            ]
        )
        vol_id = di_resp['Reservations'][0]['Instances'][0]['BlockDeviceMappings'][0]['Ebs']['VolumeId']
        az = di_resp['Reservations'][0]['Instances'][0]['Placement']['AvailabilityZone']
        dv_resp = ec2.describe_volumes(
            VolumeIds=[
                vol_id
            ]
        )
        vol_type = dv_resp['Volumes'][0]['VolumeType']
        iops = dv_resp['Volumes'][0]['Iops']
        root_device = dv_resp['Volumes'][0]['Attachments'][0]['Device']

        return vol_id, az, vol_type, iops, root_device
    except Exception as e:
        logger.error(e, exc_info=True)
        sys.exit(1)


def main():
    count = 0
    snapshots = {}

    logger.info('Region: {}'.format(region))
    logger.info('InstanceId: {}'.format(instance_id))
    logger.info('Fetching root volume of {}...'.format(instance_id))

    # Fetch root volume
    vol_id, az, vol_type, iops, root_device = fetch_root_volume()

    logger.info('VolumeId: {}'.format(vol_id))
    logger.info('Fetching snapshots of {}...'.format(vol_id))

    # Display menu with list of available snapshots
    while True:
        for snap_id, snap_date in fetch_snapshot(vol_id):
            count += 1

            print('{0})\t{1}'.format(count, snap_id))
            print('\t{}\n'.format(snap_date))

            snapshots[count] = {}
            snapshots[count]['SnapshotId'] = snap_id
            snapshots[count]['SnapshotDate'] = snap_date

        try:
            choice = int(input('Choose a snapshot [1-{}]: '.format(count)))

            if choice < 1 or choice > count:
                logger.error('Please choose between 1-{}'.format(count))
                count = 0
            else:
                logger.info('Your choice is [{0}] {1} - {2}'.format(choice, snapshots[choice]['SnapshotId'],
                                                                    snapshots[choice]['SnapshotDate']))
                break
        except ValueError:
            logger.error('Please choose between 1-{}'.format(count))
            count = 0

    # Create a new volume using snap_id
    logger.info('Creating a new volume using {}...'.format(snapshots[choice]['SnapshotId']))

    new_vol_id, new_vol_status = create_vol(snapshots[choice]['SnapshotId'], az, vol_type, iops)

    if new_vol_status == 'available':
        logger.info('NewVolumeId: {}'.format(new_vol_id))
        logger.info('NewVolumeStatus: {}'.format(new_vol_status))

    # Stop instance
    logger.info('Stopping {}...'.format(instance_id))

    stop_status = stop_instance(instance_id)

    if stop_status == 'stopped':
        logger.info('InstanceStatus: {}'.format(stop_status))

    # Detach volume
    old_vol_id = vol_id

    logger.info('OldVolumeId: {}'.format(old_vol_id))
    logger.info('Detaching old volume from {}...'.format(root_device))

    old_vol_status = detach_volume(old_vol_id, instance_id, root_device)

    if old_vol_status == 'available':
        logger.info('Old volume is now detached')

    # Attach volume
    logger.info('Attaching new volume to {0} [{1}]...'.format(instance_id, root_device))

    attach_status = attach_volume(new_vol_id, instance_id, root_device)

    if attach_status == 'in-use':
        logger.info('New volume is now attached')

    # Start instance
    logger.info('Starting {}...'.format(instance_id))

    start_status = start_instance(instance_id)

    if start_status == 'running':
        logger.info('InstanceStatus: {}'.format(start_status))
        logger.info('Task completed successfully')
        sys.exit(0)

if __name__ == '__main__':
    datetime_now = datetime.now().strftime('%Y%m%d-%H%M%S')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s - %(funcName)s - %(message)s',
        datefmt='%Y-%b-%d %I:%M:%S %p',
        handlers=[
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)

    ap = argparse.ArgumentParser(description='EBS Restore Snapshot v1.0')
    ap.add_argument('-r', '--region', help='AWS Region', required=True)
    ap.add_argument('-i', '--instance-id', help='Instance ID (i-1234567)', required=True)

    opts = ap.parse_args()

    region = opts.region
    instance_id = opts.instance_id

    main()
