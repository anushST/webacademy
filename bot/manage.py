"""Module to run bot."""
import argparse

from bot.db_queries import create_database
from bot.main import main

RUN_BOT_COMMAND = 'run_bot'
CREATE_DATABASE_COMMAND = 'create_database'


def manager() -> None:
    """Manage project."""
    parser = argparse.ArgumentParser(description="Project manager.")
    parser.add_argument('-r', '--run_bot', action='store_true',
                        help='Run bot')
    parser.add_argument('--create_database', action='store_true',
                        help='Create database')

    args = parser.parse_args()
    if args.run_bot:
        print('Bot runed. To exit use CTRL+C')
        main()
        print('Bot turned off. Bye.')
    elif args.create_database:
        create_database()
        print('Database created successfully')
    else:
        parser.print_help()


if __name__ == '__main__':
    manager()
