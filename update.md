1. `ssh` into the AWS ec2 instance
2. Activate super user with `sudo su`
3. Navigate to the path-generator directory `cd /src/whimc/path-generator`
4. Pull new files `git pull`
5. Update `config.json` with the new entries that have been added from `config-sample.json`
    1. Since this is all through the terminal, you'll have to use a tool like `vim` or `emacs` to edit the file
    2. Make sure to update the `coreprotect_id` field for each new map that was added
    3.  After updating the file, if you run `diff config.json config-sample.json`, you should just see differences for `coreprotect_id` and database/Imgur credentials
6. Run `systemctl restart path-generator` to restart the API
