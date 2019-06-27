# kkonsole

kkonsole command-line project (docker + python based) for Kentik SE/CSE to perform common tasks.

## Installation

The project is meant to be installed locally and run as a lightweight python docker container(s)

1. Download and install [Docker](https://www.docker.com/products/docker-desktop). Skip if already installed and logged in.
2. Clone the repository `git clone https://github.com/axehayz/kkonsole.git`
3. Setup environment file using [provided sample environment file](docs/sample_myenv.env)
    `cp ./docs/sample_myenv.env ./kkonsole_env.env`
    Edit the newly created `kkonsole_env.env` file and add your credentials. This *(optional)* step is used during docker-build to export the credentials as environment variables for quick access. Recommend to do it.
4. Build the container using `docker-compose build`
5. Run the container using `docker-compose run --rm kkonsole`
6. On successful run, you will land on bash shell inside the container, ready for use.

## Usage

The project is currently divided into 3 entrypoints.
> kkonsole
kperform
klookup
kstats (WIP)

All the entrypoint commands and subcommands support `--help` functionality. Feel free to explore.

### kkonsole entrypoint

This is used for most basic tasks like using API credentials from environment file to maintain a persistant login for wherever you need to use the credentials, check for new API credentials, and find what credentials are currently in use.

```bash
bash-4.4# kkonsole --help
Usage: kkonsole [OPTIONS] COMMAND [ARGS]...

  kentik konsole utility for SEs/CSEs

Options:
  --help  Show this message and exit.

Commands:
  login   Use to login or test API Credentials with --prod flag
  whoami
```

Use `kkonsole login` to evaluate necessary credentials stored in kkonsole_env.env file.

```bash
bash-4.4# kkonsole login
Api token [mykey_from_env_file]:
Api email [myemail_from_env_file]:
[INFO]: Login successful.
[INFO]: Welcome Akshay Dhawale:[74354]

bash-4.4# kkonsole whoami
[INFO]: Currently logged in as Akshay Dhawale UID:74354 CID:49769

bash-4.4# kkonsole login --api-token mykey --api-email myemail
[INFO]: Login successful.
[INFO]: Welcome Akshay Dhawale:[74354]
```

Logs are stored in `/var/log/kkonsole.log`

---

### kperform entrypoint

kperform is used to create, update, delete kentik objects via Kentik v5 API. It is *recommended* to login before issuing kperform.

```bash
bash-4.4# kperform --help
Usage: kperform [OPTIONS] COMMAND [ARGS]...

  Use kperform to add/delete/update various kentik dimensions

Options:
  --help  Show this message and exit.

Commands:
  create  create group routines for POST API methods against kentik v5 api
  delete  delete group routines (not implemented yet)
  update  update group routines (not implemented yet)
```

Emperically, `kperform create` is used the most. Here is what it looks like.

```bash
bash-4.4# kperform create --help
Usage: kperform create [OPTIONS] COMMAND [ARGS]...

  create group routines for POST API methods against kentik v5 api

Options:
  -p, --prod / --no-prod  PROD credentials.
  --help                  Show this message and exit.

Commands:
  devices        create devices
  devices-sites  create devices and sites recursively (not implemented)
  populators     create populators
  sites          create sites
  users          create users (not implemented)
```

The `kperform create` subcommands for devices, sites, etc are very self-explanatory. Each require the path to file which will be used as source_file to create the objects. Some subcommands will require other mandatory parameters. If the source_file does not contain some of the required parameters for the subcommand object in question, the program will prompt automatically or wont proceed.

```bash
bash-4.4# kkonsole whoami
[INFO]: Currently logged in as Akshay Dhawale UID:74354 CID:49769

bash-4.4# kperform create devices -f /path/does/not/resolve
Usage: kperform create devices [OPTIONS]
Try "kperform create devices --help" for help.
Error: Invalid value for "--file" / "-f": File "/path/does/not/resolve" does not exist.

bash-4.4# kperform create devices -f /kkonsole/docs/sample_createDevices.csv
```

`kperform create devices -f /kkonsole/docs/sample_createDevices.csv` will create 2 sample devices from the /kkonsole/docs/sample_createDevices.csv in the account which is logged in.

>Note:
>The source_file should be present inside the container. To use your custom .csv file as source_file, proceed to add/copy the file in the container.
>`docker cp /source_file/on/local/machine <container>:/path/inside/container/source_file`
>Find docker container using `docker container ls`

---

### klookup entrypoint

klookup helps with trivial tasks like looking up if a company has signed up for trial, find accounts using emails, company name, or company id.

Few important notes:

1. Automatic ssh keys import via docker build args or volume share is not implemented (yet). This means, you need to add/copy ssh keys and agent manually from your local machine. The code supports password and 2fa prompts.
2. Another dependency is that the code triggers a script on one of Kentik boxes to fetch results. This file must be present locally on the box. Refer to internal notes for more details.

```bash
bash-4.4# klookup --help
Usage: klookup [OPTIONS]

  Lookup accounts in usual ways. (Today) need to add ssh-keys manually.
  Make sure kkonsole_redash_butler.py exists in your $HOME on jmp01 and has
  execution rights.

Options:
  --cid INTEGER  lookup by Company ID
  --email TEXT   lookup by Email
  --cname TEXT   lookup by Company Name
  --help         Show this message and exit.
```

Copy your Kentik `~/.ssh/config` and Kentik `~/.ssh/id_rsa` to the docker container.
Start ssh agent inside the container using `eval "$(ssh-agent -s)"`
Set appropriate permissions `chmod 700 ~/.ssh/` and `chmod 600 ~/.ssh/config` `chmod 600 ~/.ssh/id_rsa`
Add the ssh-key using `ssh-add ~/.ssh/id_rsa`

Once the ssh is setup, you can issue klookup commands.

```bash
bash-4.4# klookup --email writetoakshay
Enter passphrase for key '/root/.ssh/id_rsa':
YubiKey for `adhawale':
{
  "company_name_full": "A-Corp",
  "last_login": "2018-10-01T18:05:43.977000",
  "company_id": 49769,
  "user_email": "writetoakshay@outlook.com"
}

[INFO] found a list of output with 1 items

bash-4.4#
```

---

### kstats entrypoint

kstats is new. Intend to make it a monitoring capability for individual SEs/CSEs. This will a WIP. A limited example today is below which provides last 2 snapshots of some vitals for provided CID.

```bash
bash-4.4# kstats --cid 49769
Enter passphrase for key '/root/.ssh/id_rsa':
YubiKey for `adhawale':
{
  "n_sites": 1,
  "total_contracted_fps": 6000,
  "fps_utilization_pct": 0.0,
  "n_users": 1,
  "n_populators": 0,
  "company_id": 49769,
  "fps_at_overall_p98_time": 0,
  "id": 225193,
  "n_devices_sending_flow": 0,
  "n_devices": 5
}
{
  "n_sites": 1,
  "total_contracted_fps": 6000,
  "fps_utilization_pct": 0.0,
  "n_users": 1,
  "n_populators": 0,
  "company_id": 49769,
  "fps_at_overall_p98_time": 0,
  "id": 224525,
  "n_devices_sending_flow": 0,
  "n_devices": 5
}

[INFO] found a list of output with 2 items
```

---

## Logs

Most of the functionality comes with extensive logging. Logs are present in `/var/log/*`.
Important logs come with a random (fugazy) number to lookup (read:grep) said transaction logs.

## Built with

* [Docker](https://www.docker.com/products/docker-desktop)
* [click/python](https://click.palletsprojects.com/en/7.x/)
* [requests/python](http://docs.python-requests.org/en/master/)

## Contribute

There is a [feature-wishlist](docs/feature_wishlist.txt) which contributers can help with.
Contribution guidelines will be provided soon for contributing on create/delete scripts under kperform.

## License

This project is licensed under the MIT License - see the LICENSE.md(LICENSE.md) for details.
