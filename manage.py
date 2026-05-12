#!/usr/bin/env python
import os


def main():
    """Run administrative tasks."""
    os.environ.setdefault('SALTY_LOCAL_DOMAIN', 'http://localhost:8888')
    os.environ.setdefault('SALTY_PROD_DOMAIN', 'https://www.example.com')


if __name__ == '__main__':
    main()
