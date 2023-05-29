# Job Engine

CloudBolt's task-runner and job queue.

## Architecture

### Components

The Job Engine is made up of multiple components, described below:

* CloudBolt: Django application that users interact with. Creates Jobs.
* Database: MySQL DB that serves as the queue for Jobs.
* Job: A Django object, associated with the Jobs table in the database,
  which is tied to code that is executed (e.g. provisioning a server).
* `jobengine.py`: Python file that claims Jobs, assigns them to Threads, and
  executes them.
* [Supervisor][supervisor]: Daemonized manager process that runs on the server
  and orchestrates one or more `jobengine.py` processes.

Everything in this directory (e.g. `/opt/cloudbolt/jobengine`) runs outside the
context of the running Django instance.

### Diagram

```text
+===========+       +=============+       +====================+
| CloudBolt |       | Database    |       | Supervisor         |
+===========+       +=============+       +====================+
|           |  (1)  | Job #1      |  (2)  | +--------------+   |
| Django    |------>|-------------|-------->|              |+  |
|           |<------| Job #2      |<--------| jobengine.py ||+ |
+-----------+       |-------------|       | |              ||| |
                    | Job #3      |       | +--------------+|| |
                    +-------------+       |  +--- | ^ ------+| |
                            ^             |   +-- | | (3) ---+ |
                            |             +------ | | ---------+
                            |                     v |
                            |               +==============+
                            |               | RunJobThread |
                            |    (4)        +==============+
                            +---------------| .run()       |
                                            +--------------+


(1): CloudBolt writes Jobs to the database as "PENDING". When the Job Engine
     updates a Job's status, such as when it's been queued or when it's running,
     CloudBolt reads the updated information from the database and displays it
     to the user.
(2): "PENDING" Jobs are picked up by the Job Engine, and the status is written
     back to the database when the Job completes.
(3): Queued Jobs are assigned to a thread (RunJobThread object) by jobengine.py.
     Those thread objects return their status to the jobengine.py process that
     spawned them.
(4): A Job's .run() method executes and writes progress back to the database
     throughout its lifetime.
```

### Logs

Log files can be found at `/var/log/cloudbolt/`

* Job Engine: `/var/log/cloudbolt/jobengine.log` (e.g. General logging for all
  things Job Engine)
* Job Engine Worker: `/var/log/cloudbolt/jobengine-worker0<X>.log` (e.g. A
  single `jobengine.py` process)
* Supervisor: `/var/log/cloudbolt/supervisord.log`

### Configuration

**Files**

* Job Engine: `/etc/supervisord.d/jobengine.conf`
* Supervisor: `/etc/supervisord.conf`

**Helpful Commands**

`supervisorctl [start|stop|restart] jobengine:*`
`supervisorctl status jobengine:*`
`supervisorctl reload`
`systemctl status supervisord`

[supervisor]: http://supervisord.org/

## Making and testing changes

While updating or testing job engine code, you will want to verify its behavior
outside a development environment, such as on a CIT server. In this case, you
should shutdown the supervisord process, and update and run the jobengine
manually. This will prevent caching issues with supervisord that can cause
confusing behavior. To be sure your machine is running the expected version of
your code, follow these steps:

1. Stop all running JobEngine instances. If you are in a High Availability
   environment, be sure to do this on all JobEngine instances.

   ```
   $ supervisorctl stop jobengine:*
   ```

2. Rename the existing job engine code:

    ```
    $ mv /opt/cloudbolt/jobengine/jobengine.pyc /opt/cloudbolt/jobengine/jobengine_ORIG.pyc
    ```

3. Copy (using `scp`, for example) your updated `jobengine.py` file to
   `/opt/cloudbolt/jobengine/jobengine.py` on the target server.

4. Execute your job engine file as follows:

    ```
    $ python /opt/cloudbolt/jobengine/jobengine.py --namespace=worker<int>
    ```

5. Once you are satisfied with your changes, remove the `jobengine.py` file,
  and rename the `jobengine_ORIG.pyc` file back to `jobengine.pyc`,

6. Finally, reload supervisord and restart the jobengine:

    ```
    $ supervisorctl reload
    $ supervisor start jobengine:*
    ```
