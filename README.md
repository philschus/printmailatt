# printmailatt
Python script that automatically prints mail attachments

## What does it do?

The main use case is the following: Send an email with attachments to be printed to a dedicated mail address (e.g. `printmymailatt@myprovider.com`) with the subject containing `#print`. If `printmailatt.py` is run on the machine connected to your printer it will connect to the IMAP server, download all unread mails, look for the '#print' keyword in the subject, convert all printable mail attachments to pdf, print all converted pdfs, delete the unread `#print`-mails.

Ideally, the script is run automatically, e.g. every 30 secs, on an always-on Raspberry Pi connected to your printer.

## Requriements

- Linux machine with internet connection and connected printer
- dedicated IMAP mail address
- LibreOffice, unoconv, qpdf, Python 3.x + modules

## Features

- prints: pdf, docx, pptx, text-file
- multiple attachments
- external .cfg file
- encrypted mail password
- print selected pages (e.g. #print #pages20-30)
- duplex/non-duplex (default is duplex, to deactive use: `#print #singlesided` or `#print #noduplex`)
- automatically chooses ortientation
- whitelist for sender mail addresses

## How to run

1. encrypt mail password using the MAC-address of the machine connected to the printer (optional but recommended)

    ```
    python3 generateKey.py
    ```

2. edit `default.cfg` or create your own configuration file, e.g. `myconfig.cfg` and enter the required information: printer name, server address, mail address, (encrypted) mail password, whitelisted sender mail addresses

3. run script manually

    ```
    python3 printmailatt.py myconfig.cfg
    ```
    or use the bash script (edit first to use the correct `.cfg` file)

    ```
    ./printmailatt.sh
    ```
    (probably requires `chmod +x printmailatt.sh` first). The bash script will append all script outputs to `output.log`.

## How to automatically check every 30 seconds?

A convenient way is to use `cron`. Add the following lines (with the correct user name and location of `printmailatt.sh`) in `/etc/crontab`

```
# run bash script every 30 seconds
*/1 * * * * pi /home/pi/printmailatt/printmailatt.sh
*/1 * * * * pi ( sleep 30 ; /home/pi/printmailatt/printmail.sh )
```

