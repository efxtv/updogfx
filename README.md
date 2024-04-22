![Version 1.0](http://img.shields.io/badge/version-v1.4-green.svg)
![Python 3](http://img.shields.io/badge/python-3.8-blue.svg)

<p>
  <img src="#" width=85px alt="UPDOGFX"/>
</p>

Now updog is supported in Termux (termux updog).
We developed updogfx to be compatible with Termux, requiring minimal resources. 
It serves as a replacement for Python's `SimpleHTTPServer`. Updogfx facilitates uploading and downloading via HTTP/S with the help of an Android browser.

[JOIN us on Telegram](https://t.me/efxtv)

<p align="center">
  <img src="#" alt="Updogfx screenshot"/>
</p>

## Installation

Install using commands:

`mkdir $PREFIX/opt/updog;git clone https://giturl.git $PREFIX/opt/;cd $PREFIX/opt/updogfx`

`bash install.sh`

`updogfx`

## Usage

`updog [-d DIRECTORY] [-p PORT] [--password PASSWORD] [--ssl]`

| Argument                            | Description                                      |
|-------------------------------------|--------------------------------------------------| 
| -d DIRECTORY, --directory DIRECTORY | Path to upload folder [Default=current directory]| 
| -p PORT, --port PORT                | Port number to listen on (default: 8080)         |
| -h, --help                          | Show help                                        |

## Examples

**Serve from your current directory:**

`updog`

**Serve from another directory:**

`updog -d /another/directory`

**Serve from port 8080:**

# Donate
---------------------------------------
# Donate
<a href="#"><img src="https://raw.githubusercontent.com/efxtv/EFX-Tv-Bookmarks/main/bin/DONATE/USDT.png" title="Please donate to support EFX Tv" alt="CryptoUSDT" width="241" height="269"></a>

## Thanks

Inspired by the [Updog](https://github.com/sc0tfree/updog)
