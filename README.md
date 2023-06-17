# Bulk Downloader for Reddit x

[![PyPI Status](https://img.shields.io/pypi/status/bdfrx?logo=PyPI)](https://pypi.python.org/pypi/bdfrx)
[![PyPI version](https://img.shields.io/pypi/v/bdfrx.svg?logo=PyPI)](https://pypi.python.org/pypi/bdfrx)
[![Python Test](https://github.com/OMEGARAZER/bulk-downloader-for-reddit-x/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/OMEGARAZER/bulk-downloader-for-reddit-x/actions/workflows/test.yml)
[![linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&label=linting)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?logo=Python)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

This is a tool to download submissions from Reddit. BDFRx is flexible and can be used in scripts if needed through an extensive command-line interface. [List of currently supported sources](#list-of-currently-supported-sources)

If you wish to open an issue, please read [the guide on opening issues](docs/CONTRIBUTING.md#opening-an-issue) to ensure that your issue is clear and contains everything it needs to for the developers to investigate.

Included in this README are a few example Bash tricks to get certain behaviour. For that, see [Common Command Tricks](#common-command-tricks).

## Installation

*Bulk Downloader for Reddit x* needs Python version 3.9 or above. Please update Python before installation to meet the requirement.

Then, you can install it via [pipx](https://pypa.github.io/pipx) with:

```bash
pipx install bdfrx
```

or via pip with:

```bash
python3 -m pip install bdfrx --upgrade
```

**To update BDFRx**, run the above command again for pip or `pipx upgrade bdfrx` for pipx installations.

**To check your version of BDFRx**, run `bdfrx --version`

**To install shell completions**, run `bdfrx completion`

### Source code

If you want to use the source code or make contributions, refer to [CONTRIBUTING](docs/CONTRIBUTING.md#preparing-the-environment-for-development)

## **Differences from [BDFR](https://github.com/aliparlakci/bulk-downloader-for-reddit)**

BDFRx differs from the base BDFR in a few ways:

- Does not contain the Archive and Clone modes (If you require these modes you can try v0.9.1, provided *as is* or use the base [BDFR](https://github.com/aliparlakci/bulk-downloader-for-reddit) project)
- Option to use an Sqlite3 database to store hashes, links and post ID's to be filtered in future runs
- Uses the `bdfrx` config directory by default

## Reddit API Changes

Starting July 1st 2023 ([along with the other changes](https://reddit.com/12qwagm)) rate limits will be [applied ***per client id*** rather than by client id/user combination](https://reddit.com/13wsiks). Therefore it is no longer tenable to ship BDFRx with an installed client id as it will cause rate limiting for all users. **The shipped client id will no longer be valid after the changes.**

To create your own for use with BDFRx go [here](https://old.reddit.com/prefs/apps/) and click "create an app". It's recommended to choose "Installed App" and use "http://localhost:7634" as the redirect url. <!-- markdownlint-disable-line MD034 -->

Once you have your personal client id add it to your [config.cfg](bdfrx/default_config.cfg) at the location in the [configuration](#configuration) section.

## Usage

BDFRx works by taking submissions from a variety of "sources" from Reddit and then parsing them to download. These sources might be a subreddit, multireddit, a user list, or individual links. These sources are combined and downloaded to disk, according to a naming and organisational scheme defined by the user.

The sole mode of BDFRx is download. The `download` command will download the resource linked in the Reddit submission, such as the images, video, etc.

After installation, run the program from any directory as shown below:

```bash
bdfrx download
```

However, this command is not enough. You should chain parameters in [Options](#options) according to your use case. Don't forget that some parameters can be provided multiple times. Some quick reference commands are:

```bash
bdfrx download ./path/to/output --subreddit Python -L 10
```

```bash
bdfrx download ./path/to/output --user reddituser --submitted -L 100
```

```bash
bdfrx download ./path/to/output --user me --saved --authenticate -L 25 --file-scheme "{POSTID}"
```

```bash
bdfrx download ./path/to/output --subreddit "Python, all, mindustry" -L 10 --make-hard-links
```

Alternatively, you can pass options through a YAML file.

```bash
bdfrx download ./path/to/output --opts my_opts.yaml
```

For example, running it with the following file

```yaml
skip: [mp4, avi]
file_scheme: "{UPVOTES}_{REDDITOR}_{POSTID}_{DATE}"
limit: 10
sort: top
subreddit:
  - EarthPorn
  - CityPorn
```

would be equilavent to (take note that in YAML there is `file_scheme` instead of `file-scheme`):

```bash
bdfrx download ./path/to/output --skip mp4 --skip avi --file-scheme "{UPVOTES}_{REDDITOR}_{POSTID}_{DATE}" -L 10 -S top --subreddit EarthPorn --subreddit CityPorn
```

Any option that can be specified multiple times should be formatted like subreddit is above.

In cases when the same option is specified both in the YAML file and in as a command line argument, the command line argument takes priority

## Options

- `directory`
    - This is the directory to which BDFRx will download and place all files
- `--authenticate`
    - This flag will make BDFRx attempt to use an authenticated Reddit session
    - See [Authentication](#authentication-and-security) for more details
- `--config`
    - If the path to a configuration file is supplied with this option, BDFRx will use the specified config
    - See [Configuration Files](#configuration) for more details
- `--db`
    - Connects to a sqlite3 db to save hashes, paths and links to be reused
    - Automatically sets no-dupes to enabled using saved hashes
    - Allows hard links to be created with paths based on saved hashes
    - Saves links so they are skipped from downloading in the future
    - Complements exclude-id options but does not require them
- `--db-file`
    - Allows to specify a location of the sqlite3 db rather than storing in the config directory
- `--disable-module`
    - Can be specified multiple times
    - Disables certain modules from being used
    - See [Disabling Modules](#disabling-modules) for more information and a list of module names
- `--downvoted`
    - This will use a user's downvoted posts as a source of posts to scrape
    - This requires an authenticated Reddit instance, using the `--authenticate` flag, as well as `--user` set to `me`
- `--exclude-id`
    - This will skip the download of any submission with the ID provided
    - Can be specified multiple times
- `--exclude-id-file`
    - This will skip the download of any submission with any of the IDs in the files provided
    - Can be specified multiple times
    - Format is one ID per line
- `--file-scheme`
    - Sets the scheme for files
    - Default is `{REDDITOR}_{TITLE}_{POSTID}`
    - See [Folder and File Name Schemes](#folder-and-file-name-schemes) for more details
- `--filename-restriction-scheme`
    - Can be: `windows`, `linux`
    - Turns off the OS detection and specifies which system to use when making filenames
    - See [Filesystem Restrictions](#filesystem-restrictions)
- `--folder-scheme`
    - Sets the scheme for folders
    - Default is `{SUBREDDIT}`
    - See [Folder and File Name Schemes](#folder-and-file-name-schemes) for more details
- `--ignore-user`
    - This will add a user to ignore
    - Can be specified multiple times
- `--include-id-file`
    - This will add any submission with the IDs in the files provided
    - Can be specified multiple times
    - Format is one ID per line
- `-L, --limit`
    - This is the limit on the number of submissions retrieve
    - Default is max possible
    - Note that this limit applies to **each source individually** e.g. if a `--limit` of 10 and three subreddits are provided, then 30 total submissions will be scraped
    - If it is not supplied, then BDFRx will default to the maximum allowed by Reddit, roughly 1000 posts. **This cannot be bypassed.**
- `-l, --link`
    - This is a direct link to a submission to download, either as a URL or an ID
    - Can be specified multiple times
- `--log`
    - This allows one to specify the location of the logfile
    - This must be done when running multiple instances of BDFRx, see [Multiple Instances](#multiple-instances) below
- `--make-hard-links`
    - This flag will create hard links to an existing file when a duplicate is downloaded in the current run
    - This will make the file appear in multiple directories while only taking the space of a single instance
- `--max-wait-time`
    - This option specifies the maximum wait time for downloading a resource
    - The default is 120 seconds
    - See [Rate Limiting](#rate-limiting) for details
- `--min-score`
    - This skips all submissions which have fewer than specified upvotes
- `--max-score`
    - This skips all submissions which have more than specified upvotes
- `--min-score-ratio`
    - This skips all submissions which have lower than specified upvote ratio
- `--max-score-ratio`
    - This skips all submissions which have higher than specified upvote ratio
- `-m, --multireddit`
    - This is the name of a multireddit to add as a source
    - Can be specified multiple times
        - This can be done by using `-m` multiple times
        - Multireddits can also be used to provide CSV multireddits e.g. `-m "chess, favourites"`
    - The specified multireddits must all belong to the user specified with the `--user` option
- `--no-dupes`
    - This flag will skip writing a file to disk if that file was already downloaded in the current run
    - This is calculated by MD5 hash
- `--opts`
    - Load options from a YAML file.
    - Has higher prority than the global config file but lower than command-line arguments.
    - See [opts_example.yaml](./opts_example.yaml) for an example file.
- `--saved`
    - This option will make BDFRx use the supplied user's saved posts list as a download source
    - This requires an authenticated Reddit instance, using the `--authenticate` flag, as well as `--user` set to `me`
- `--search`
    - This will apply the input search term to specific lists when scraping submissions
    - A search term can only be applied when using the `--subreddit` and `--multireddit` flags
- `--search-existing`
    - This will make BDFRx compile the hashes for every file in `directory`
    - The hashes are used to skip duplicate files if `--no-dupes` is supplied or make hard links if `--make-hard-links` is supplied
    - **The use of this option is highly discouraged due to inefficiency**
- `--skip`
    - This adds file types to the download filter i.e. submissions with one of the supplied file extensions will not be downloaded
    - Can be specified multiple times
- `--skip-domain`
    - This adds domains to the download filter i.e. submissions coming from these domains will not be downloaded
    - Can be specified multiple times
    - Domains must be supplied in the form `example.com` or `img.example.com`
- `--skip-subreddit`
    - This skips all submissions from the specified subreddit
    - Can be specified multiple times
    - Also accepts CSV subreddit names
- `-S, --sort`
    - This is the sort type for each applicable submission source supplied to BDFRx
    - This option does not apply to upvoted, downvoted or saved posts when scraping from these sources
    - The following options are available:
        - `controversial`
        - `hot` (default)
        - `new`
        - `relevance` (only available when using `--search`)
        - `rising`
        - `top`
- `--submitted`
    - This will use a user's submissions as a source
    - A user must be specified with `--user`
- `-s, --subreddit`
    - This adds a subreddit as a source
    - Can be used mutliple times
        - This can be done by using `-s` multiple times
        - Subreddits can also be used to provide CSV subreddits e.g. `-m "all, python, mindustry"`
- `-t, --time`
    - This is the time filter that will be applied to all applicable sources
    - This option does not apply to upvoted, downvoted or saved posts when scraping from these sources
    - This option only applies if sorting by top or controversial.  See --sort for more detail.
    - The following options are available:
        - `all` (default)
        - `hour`
        - `day`
        - `week`
        - `month`
        - `year`
    - `--time-format`
        - This specifies the format of the datetime string that replaces `{DATE}` in file and folder naming schemes
        - See [Time Formatting Customisation](#time-formatting-customisation) for more details, and the formatting scheme
- `--upvoted`
    - This will use a user's upvoted posts as a source of posts to scrape
    - This requires an authenticated Reddit instance, using the `--authenticate` flag, as well as `--user` set to `me`
- `-u, --user`
    - This specifies the user to scrape in concert with other options
    - When using `--authenticate`, `--user me` can be used to refer to the authenticated user
    - Can be specified multiple times for multiple users
        - If downloading a multireddit, only one user can be specified
- `-v, --verbose`
    - Increases the verbosity of the program
    - Can be specified multiple times

## Common Command Tricks

A common use case is for subreddits/users to be loaded from a file. BDFRx supports this via YAML file options (`--opts my_opts.yaml`).

Alternatively, you can use the command-line [xargs](https://en.wikipedia.org/wiki/Xargs) function.
For a list of users `users.txt` (one user per line), type:

```bash
cat users.txt | xargs -L 1 echo --user | xargs -L 50 bdfrx download <ARGS>
```

The part `-L 50` is to make sure that the character limit for a single line isn't exceeded, but may not be necessary. This can also be used to load subreddits from a file, simply exchange `--user` with `--subreddit` and so on.

## Authentication and Security

BDFRx uses OAuth2 authentication to connect to Reddit if authentication is required. This means that it is a secure, token-based system for making requests. This also means that BDFRx only has access to specific parts of the account authenticated, by default only saved posts, upvoted posts, downvoted posts, and the identity of the authenticated account. Note that authentication is not required unless accessing private things like upvoted posts, downvoted posts, saved posts, and private multireddits.

To authenticate, BDFRx will first look for a token in the configuration file that signals that there's been a previous authentication. If this is not there, then BDFRx will attempt to register itself with your account. This is normal, and if you run the program, it will pause and show a Reddit URL. Click on this URL and it will take you to Reddit, where the permissions being requested will be shown. Read this and **confirm that there are no more permissions than needed to run the program**. You should not grant unneeded permissions; by default, BDFRx only requests permission to read your saved, upvoted, or downvoted submissions and identify as you.

If the permissions look safe, confirm it, and BDFRx will save a token that will allow it to authenticate with Reddit from then on.

## Changing Permissions

Most users will not need to do anything extra to use any of the current features. However, if additional features such as scraping messages, PMs, etc are added in the future, these will require additional scopes. Additionally, advanced users may wish to use BDFRx with their own API key and secret. There is normally no need to do this, but it *is* allowed by BDFRx.

The configuration file for BDFRx contains the API secret and key, as well as the scopes that BDFRx will request when registering itself to a Reddit account via OAuth2. These can all be changed if the user wishes, however do not do so if you don't know what you are doing. The defaults are specifically chosen to have a very low security risk if your token were to be compromised, however unlikely that actually is. Never grant more permissions than you absolutely need.

For more details on the configuration file and the values therein, see [Configuration Files](#configuration).

## Folder and File Name Schemes

The naming and folder schemes for BDFRx are both completely customisable. A number of different fields can be given which will be replaced with properties from a submission when downloading it. The scheme format takes the form of `{KEY}`, where `KEY` is a string from the below list.

- `DATE`
- `FLAIR`
- `POSTID`
- `REDDITOR`
- `SUBREDDIT`
- `TITLE`
- `UPVOTES`

Each of these can be enclosed in curly bracket, `{}`, and included in the name. For example, to just title every downloaded post with the unique submission ID, you can use `{POSTID}`. Static strings can also be included, such as `download_{POSTID}` which will not change from submission to submission. For example, the previous string will result in the following submission file names:

- `download_aaaaaa.png`
- `download_bbbbbb.png`

At least one key *must* be included in the file scheme, otherwise an error will be thrown. The folder scheme however, can be null or a simple static string. In the former case, all files will be placed in the folder specified with the `directory` argument. If the folder scheme is a static string, then all submissions will be placed in a folder of that name. In both cases, there will be no separation between all submissions.

It is highly recommended that the file name scheme contain the parameter `{POSTID}` as this is **the only parameter guaranteed to be unique**. No combination of other keys will necessarily be unique and may result in posts being skipped as BDFRx will see files by the same name and skip the download, assuming that they are already downloaded.

## Configuration

The configuration files are, by default, stored in the configuration directory for the user. This differs depending on the OS that BDFRx is being run on. For Windows, this will be:

- `C:\Users\<User>\AppData\Local\BDFRx\bdfrx`

If Python has been installed through the Windows Store, the folder will appear in a different place. Note that the hash included in the file path may change from installation to installation.

- `C:\Users\<User>\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\Local\BDFRx\bdfrx`

On Mac OSX, this will be:

- `~/Library/Application Support/bdfrx`.

Lastly, on a Linux system, this will be:

- `~/.config/bdfrx/`

The logging output for each run of BDFRx will be saved to this directory in the file `log_output.txt`. If you need to submit a bug, it is this file that you will need to submit with the report.

### Configuration File

The `config.cfg` is the file that supplies BDFRx with the configuration to use. At the moment, the following keys **must** be included in the configuration file supplied.

- `client_id`
- `scopes`

The following key may be required depending on the type of client id you created.

- `client_secret`

The following keys are optional, and defaults will be used if they cannot be found.

- `backup_log_count`
- `max_wait_time`
- `time_format`
- `disabled_modules`
- `filename-restriction-scheme`

All of these should not be modified unless you know what you're doing, as the default values will enable BDFRx to function just fine. A configuration is included in BDFRx when it is installed, and this will be placed in the configuration directory as the default.

Most of these values have to do with OAuth2 configuration and authorisation. The key `backup_log_count` however has to do with the log rollover. The logs in the configuration directory can be verbose and for long runs of BDFRx, can grow quite large. To combat this, BDFRx will overwrite previous logs. This value determines how many previous run logs will be kept. The default is 3, which means that BDFRx will keep at most three past logs plus the current one. Any runs past this will overwrite the oldest log file, called "rolling over". If you want more records of past runs, increase this number.

#### Time Formatting Customisation

The option `time_format` will specify the format of the timestamp that replaces `{DATE}` in filename and folder name schemes. By default, this is the [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) format which is highly recommended due to its standardised nature. If you don't **need** to change it, it is recommended that you do not. However, you can specify it to anything required with this option. The `--time-format` option supersedes any specification in the configuration file

The format can be specified through the [format codes](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior) that are standard in the Python `datetime` library.

#### Disabling Modules

The individual modules of BDFRx, used to download submissions from websites, can be disabled. This is helpful especially in the case of the fallback downloaders, since the `--skip-domain` option cannot be effectively used in these cases. For example, the Youtube-DL downloader can retrieve data from hundreds of websites and domains; thus the only way to fully disable it is via the `--disable-module` option.

Modules can be disabled through the command line interface for BDFRx or more permanently in the configuration file via the `disabled_modules` option. The list of downloaders that can be disabled are the following. Note that they are case-insensitive.

- `Direct`
- `DelayForReddit`
- `Erome`
- `Gallery` (Reddit Image Galleries)
- `Gfycat`
- `Imgur`
- `PornHub`
- `Redgifs`
- `SelfPost` (Reddit Text Post)
- `Vidble`
- `VReddit` (Reddit Video Post)
- `Youtube`
- `YtdlpFallback` (Youtube DL Fallback)

### Rate Limiting

The option `max_wait_time` has to do with retrying downloads. There are certain HTTP errors that mean that no amount of requests will return the wanted data, but some errors are from rate-limiting. This is when a single client is making so many requests that the remote website cuts the client off to preserve the function of the site. This is a common situation when downloading many resources from the same site. It is polite and best practice to obey the website's wishes in these cases.

To this end, BDFRx will sleep for a time before retrying the download, giving the remote server time to "rest". This is done in 60 second increments. For example, if a rate-limiting-related error is given, BDFRx will sleep for 60 seconds before retrying. Then, if the same type of error occurs, it will sleep for another 120 seconds, then 180 seconds, and so on.

The option `--max-wait-time` and the configuration option `max_wait_time` both specify the maximum time BDFRx will wait. If both are present, the command-line option takes precedence. For instance, the default is 120, so BDFRx will wait for 60 seconds, then 120 seconds, and then move one. **Note that this results in a total time of 180 seconds trying the same download**. If you wish to try to bypass the rate-limiting system on the remote site, increasing the maximum wait time may help. However, note that the actual wait times increase exponentially if the resource is not downloaded i.e. specifying a max value of 300 (5 minutes), can make BDFRx pause for 15 minutes on one submission, not 5, in the worst case.

## Multiple Instances

BDFRx can be run in multiple instances with multiple configurations, either concurrently or consecutively. The use of scripting files facilitates this the easiest, either Powershell on Windows operating systems or Bash elsewhere. This allows multiple scenarios to be run with data being scraped from different sources, as any two sets of scenarios might be mutually exclusive i.e. it is not possible to download any combination of data from a single run of BDFRx. To download from multiple users for example, multiple runs of BDFRx are required.

Running these scenarios consecutively is done easily, like any single run. Configuration files that differ may be specified with the `--config` option to switch between tokens, for example. Otherwise, almost all configuration for data sources can be specified per-run through the command line.

Running scenarios concurrently (at the same time) however, is more complicated. BDFRx will look to a single, static place to put the detailed log files, in a directory with the configuration file specified above. If there are multiple instances, or processes, of BDFRx running at the same time, they will all be trying to write to a single file. On Linux and other UNIX based operating systems, this will succeed, though there is a substantial risk that the logfile will be useless due to garbled and jumbled data. On Windows however, attempting this will raise an error that crashes the program as Windows forbids multiple processes from accessing the same file.

The way to fix this is to use the `--log` option to manually specify where the logfile is to be stored. If the given location is unique to each instance of BDFRx, then it will run fine.

## Filesystem Restrictions

Different filesystems have different restrictions for what files and directories can be named. Thesse are separated into two broad categories: Linux-based filesystems, which have very few restrictions; and Windows-based filesystems, which are much more restrictive in terms if forbidden characters and length of paths.

During the normal course of operation, BDFRx detects what filesystem it is running on and formats any filenames and directories to conform to the rules that are expected of it. However, there are cases where this will fail. When running on a Linux-based machine, or another system where the home filesystem is permissive, and accessing a share or drive with a less permissive system, BDFRx will assume that the *home* filesystem's rules apply. For example, when downloading to a SAMBA share from Ubuntu, there will be errors as SAMBA is more restrictive than Ubuntu.

The best option would be to always download to a filesystem that is as permission as possible, such as an NFS share or ext4 drive. However, when this is not possible, BDFRx allows for the restriction scheme to be manually specified at either the command-line or in the configuration file. At the command-line, this is done with `--filename-restriction-scheme windows`, or else an option by the same name in the configuration file.

## Manipulating Logfiles

The logfiles that BDFRx outputs are consistent and quite detailed and in a format that is amenable to regex. To this end, a number of bash scripts have been [included here](./scripts). They show examples for how to extract successfully downloaded IDs, failed IDs, and more besides.

## Unsaving posts

Back in BDFR v1 there was an option to unsave posts from your account when downloading, but it was removed from the core BDFR on v2 as it is considered a read-only tool. However, for those missing this functionality, a script was created that uses the log files to achieve this. There is info on how to use this on the README.md file on the scripts subdirectory.

## List of currently supported sources

- Direct links (links leading to a file)
- Delay for Reddit
- Erome
- Gfycat
- Gif Delivery Network
- Imgur
- Reddit Galleries
- Reddit Text Posts
- Reddit Videos
- Redgifs
- Vidble
- YouTube
    - Any source supported by [YT-DLP](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) should be compatable

## Contributing

If you wish to contribute, see [Contributing](docs/CONTRIBUTING.md) for more information.

When reporting any issues or interacting with the developers, please follow the [Code of Conduct](docs/CODE_OF_CONDUCT.md).
