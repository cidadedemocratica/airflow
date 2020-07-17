# -*- coding: utf-8 -*-

from app import App


def start_server():
    dash = App()
    dash.render()
    dash.app.run_server(debug=True, host='0.0.0.0')


if __name__ == '__main__':
    start_server()
