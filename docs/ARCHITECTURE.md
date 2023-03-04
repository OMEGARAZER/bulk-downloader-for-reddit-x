# Architecture

When the BDFR project was rewritten for v2, the goal was to make the codebase easily extensible and much easier to read and modify. However, this document provides a step-by-step look through the process that the BDFRx goes through, so that any prospective developers can more easily grasp the way the code works.

## Design Ethos

The BDFRv2 project was designed to be a stateless downloader. This means that the state of the program is forgotten between each run of the program. There are no central lists, databases, or indices, that BDFRv2 uses, only the actual files on disk. There are several advantages to this approach:

1. There is no chance of the database being corrupted or changed by something other than BDFRv2, rendering BDFRv2's "idea" of the archive wrong or incomplete.
2. Any information about the archive is contained by the archive itself i.e. for a list of all submission IDs in the archive, this can be extracted from the names of the files in said archive, assuming an appropriate naming scheme was used.
3. Archives can be merged, split, or editing without worrying about having to update a central database
4. There are no versioning issues between updates of BDFRv2, where old version are stuck with a worse form of the database
5. An archive can be put on a USB, moved to another computer with possibly a very different BDFRv2 version, and work completely fine

Another major part of the ethos of the design is DOTADIW, Do One Thing And Do It Well. It's a major part of Unix philosophy and states that each tool should have a well-defined, limited purpose. To this end, BDFRv2 is, as the name implies, a *downloader*. That is the scope of the tool. Managing the files downloaded can be for better-suited programs, since BDFRv2 is not a file manager. Nor does BDFRv2 concern itself with how any of the data downloaded is displayed, changed, parsed, or analysed. This makes BDFRv2 suitable for data science-related tasks, archiving, personal downloads, or analysis of various Reddit sources as BDFRv2 is completely agnostic on how the data is used.

## Design changes from BDFRv2

BDFRx adds the ability, but not the requirement, of using a sqlite3 db to store information between each run of the program. As it is not built into the operation of BDFRx if you need to operate statelessly you can simply omit the option to use the db file.

The other design departure is the depreciation of the Archive and Clone options. If you are in need of these functions you can find them in BDFRx versions <1.0 or in the base BDFR project.

## The Download Process

The BDFRx is organised around a central object, the RedditDownloader class.

1. The RedditDownloader parses all the arguments and configuration options, held in the Configuration object, and creates a variety of internal objects for use, such as the file name formatter, download filter, etc.
2. The RedditDownloader scrapes raw submissions from Reddit via several methods relating to different sources. A source is defined as a single stream of submissions from a subreddit, multireddit, or user list.
3. These raw submissions are passed to the DownloaderFactory class to select the specialised downloader class to use. Each of these are for a specific website or link type, with some catch-all classes like Direct.
4. The BaseDownloader child, spawned by DownloaderFactory, takes the link and does any necessary processing to find the direct link to the actual resource.
5. This is returned to the RedditDownloader in the form of a Resource object. This holds the URL and some other information for the final resource.
6. The Resource is passed through the DownloadFilter instantiated in step 1.
7. The destination file name for the Resource is calculated. If it already exists, or is marked to be excluded, then the Resource will be discarded.
8. Here the actual data is downloaded to the Resource and a hash calculated which is used to find duplicates.
9. Only then is the Resource written to the disk.

This is the step-by-step process that BDFRx goes through to download a Reddit post.

## Adding another Supported Site

This is one of the easiest changes to do with the code. First, any new class must inherit from the BaseDownloader class which provided an abstract parent to implement. However, take note of the other classes as well. Many downloaders can inherit from one another instead of just the BaseDownloader. For example, the VReddit class, used for downloading video from Reddit, inherits almost all of its code from the YouTube class. **Minimise code duplication wherever possible**.

Once the downloader class has been written **and tests added** for it as well, then the regex string for the site's URLs can be added to the DownloaderFactory. Then additional tests must be added for the DownloadFactory to ensure that the appropriate classes are called when the right URLs are passed to the factory.

## Adding Other Features

For a fundamentally different form of execution path for the program, it is best to inherit from the RedditDownloader class and override or add functionality as needed.
