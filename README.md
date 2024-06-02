# ufw-banlist-block

### Description
Janky python script to backup/restore UFW rules and add malicous IP addresses from the [Binary defence banlist](https://www.binarydefense.com/banlist.txt)

### Add path to UFW backup

- Change line 6 of the script to reflect where you want to store the UFW backup

### Setting Up a Daily Cron Job

To run this script daily as root, you can set up a cron job. Here’s how you can do it:

- Open the root user's crontab editor:

    ```sh
   sudo crontab -e
    ```

- Add the following line to run the script daily at a specified time (e.g., at midnight):

  ```sh
  0 0 * * * /usr/bin/python3 /path/to/block.py
  ```

Replace /usr/bin/python3 with the path to your Python interpreter and /path/to/block_ips.py with the path to your script.
### Note

- Ensure that the script has executable permissions:
    ```sh
    chmod +x /path/to/block.py
    ```

This setup will reset UFW rules and block the IPs from the list daily.
