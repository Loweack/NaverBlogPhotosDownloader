## Naver Blog Photos Downloader

This Python tool allows you to download full-resolution photos from blogs on Naver.
This is a fork of [NiceFlight's blogNaverPicsDownloader](https://github.com/NiceFlight/blogNaverPicsDownloader).

If you encounter any problem with the Naver Blog Photos Downloader, feel free to [open an issue](https://github.com/Loweack/NaverBlogPhotosDownloader/issues).

## How to use it

1. Install Python 3 and its pip module, and Git if they haven't been installed yet.

   `sudo apt install python3`

   `sudo apt install python-is-python3`
   
   `sudo apt install python3-pip`

   `sudo apt install git`

2. Install the required Python module.

   `pip install selenium beautifulsoup4 requests webdriver-manager --break-system-packages`

3. Clone this repository.
   
   `git clone https://github.com/Loweack/NaverBlogPhotosDownloader.git`

4. To prevent any permission issues, simply set the folder's permissions to 777 (though this is not secure, it eliminates most potential rights-related problems).

   `sudo chmod -R 777 NaverBlogPhotosDownloader`

5. Run the main Python script.

   1. If you want the interactive version.

      `python NaverBlogPhotosDownloaderInteractive.py`

   2. If you want the direct version (the command below is just an example).

      `python NaverBlogPhotosDownloaderDirect.py "https://blog.naver.com/PostView.naver?blogId=edament&logNo=223835807940&categoryNo=9&parentCategoryNo=0&viewDate=&currentPage=1&postListTopCurrentPage=&from=postList"`

   3. If you want the batch version (a text file named "url.txt" must be created in the same directory as "NaverBlogPhotosDownloaderBatch.py." In this file, you should add the URLs of the Naver blogs, with each URL on a separate line). In this edition, each download is retried three (3) times in the event of an error, and all actions are recorded in a log file (download.log).

      `python NaverBlogPhotosDownloaderBatch.py url.txt`
