# torrenttools

This is a set of scripts I used to manage to my torrent client. It will

 * `--walk`: Walk your dump directory for new files. If it detects episodes, these will be moved to the collection, sorted by show name and season.
 * `--remove-torrents`: Removes finished torrents from transmission (those that have reached their seed limits)

The scripts are geared towards Transmission (and has a simple client for the Transmission RPC protocol). But file moving feature is client-agnostic and operates on files. The scripts use [guessit](https://github.com/wackou/guessit) to parse filenames, but only supports episodes as-it.

I use [flexget](http://flexget.com/) to download `.torrent` files, which transmission then picks up. 

## Usage

Cronjob:

```
*/30 * * * * /usr/bin/python /path/to/transmissiontools.py --walk --remove-torrents > /dev/null
```

## Disclaimer

Torrents have other purposes than illegal piracy. 
