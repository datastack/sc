import argparse
import logging
import os
import subprocess

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Execute Ansible script to create and setup ssh authorization.')
parser.add_argument('--ssh-user', type=str, help='the username used by Ansible to connect on destination instance.')
parser.add_argument('--prv-key', type=str, help='a private key file already authorized to connect on destination.')
parser.add_argument('--dst-host', type=str, help='the destination hostname or ip address.')
parser.add_argument('--pub-key', type=str, help='the public key file to be added as authorized_key.')
parser.add_argument('--user-name', type=str, help='the username to be created.')
args = parser.parse_args()

playbook = os.path.dirname(os.path.realpath(__file__)) + "/ansible/playbook.yml"


def initial_check():
    logger.info('Executing initial check...')
    if not args.ssh_user:
        raise argparse.ArgumentError(args.ssh_user, 'Missing argument. Please set --ssh_user')
    if not args.prv_key:
        raise argparse.ArgumentError(args.prv_key, 'Missing argument. Please set --prv-key')
    if not args.dst_host:
        raise argparse.ArgumentError(args.dst_host, 'Missing argument. Please set --dst-host')
    if not args.pub_key:
        raise argparse.ArgumentError(args.pub_key, 'Missing argument. Please set --pub-key')
    if not args.user_name:
        raise argparse.ArgumentError(args.user_name, 'Missing argument. Please set --user-name')

    if not playbook:
        raise Exception("Ansible playbook file not found")

    ans_check = subprocess.Popen((["which", "ansible-playbook"]),
                                 stderr=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
    if not ans_check.stdout.read():
        raise Exception("Ansible executable was not found. Please check shell PATH or install it")
    logger.info('Done.')


def main():
    initial_check()
    logger.info('Starting Ansible execution...')
    ans = subprocess.Popen((["ansible-playbook",
                             "-b",
                             f"-i {args.dst_host},",
                             f"-u {args.ssh_user}",
                             f"--private-key={args.prv_key}",
                             f"-e user_name={args.user_name}",
                             f"-e key_file={args.pub_key}",
                             f"{playbook}"]),
                           stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           universal_newlines=True)

    out, err = ans.communicate(timeout=30)
    ret_code = ans.returncode

    if ret_code != 0:
        logger.exception(err)
        raise Exception("Error executing Ansible script. Please check de output information and try again.")

    logger.info(out)
    logger.info("Ansible script sucessfully executed")


if __name__ == '__main__':
    main()
