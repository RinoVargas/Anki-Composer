import sys

def main():
    if len(sys.argv) > 1:
        from frontend.cli import cli_app
        cli_app.run()
    else:
        from frontend.gui import gui_app
        gui_app.run()

if __name__ == "__main__":
    main()
