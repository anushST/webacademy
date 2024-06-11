# WEB_ACADEMY_BOT
WEB_ACADEMY_BOT
### How to run the project:

Clone repository and go to it:

```
git clone git@github.com:anushST/webacademy.git
```

```
cd webacademy
```

Create and activate virtual environment:

```
python -m venv venv
```

* If you have Linux/macOS

    ```
    source venv/bin/activate
    ```

* If you have windows

    ```
    source venv/Scripts/activate
    ```

```
python -m pip install --upgrade pip
```

Install dependencies from file requirements.txt:

```
pip install -r requirements.txt
```

Go to bot directory

```
cd bot
```

Create database

```
python manage.py --create_database
```

run bot

```
python manage.py -r
```
