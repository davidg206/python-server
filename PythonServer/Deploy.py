import random
import string
import subprocess

def generate_random_string():
    letters = string.ascii_letters
    digits = string.digits

    first_char = random.choice(letters)
    rest_chars = random.choices(letters + digits, k=8)

    random_string = ''.join([first_char] + rest_chars)
    random_string = ''.join(random.sample(random_string, len(random_string)))

    return random_string

def make_new_application(branch):
  application = generate_random_string().lower()
  subprocess.run(f'sps-app deploy ./Saved/StagedBuilds -b {application} --firebase --owner {branch}')

  host = 'david@palatial.tenant-palatial-platform.coreweave.cloud'
  subprocess.run(f'ssh {host} sudo -E python3 ~/link-deployment/run_pipeline.py {branch} {application}')

#, shell=True, capture_output=True)
