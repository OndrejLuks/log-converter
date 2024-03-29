# This script takes all the MF4 files from SourceMF4 folder, extracts CAN message using DBC files from DBCfiles
# folder and uploads these extracted data into specified database.
# For database settings change according lines in config.json file.
# It is also possible to aggregate extracted data by adjusting the setting "aggregate" inside config.json to true.
#
# Made by Ondrej Luks, 2023
# ondrej.luks@doosan.com


# ==========================================================================================================================
# ==========================================================================================================================


from src import gui, gui_interface, defs
import warnings
import multiprocessing

multiprocessing.freeze_support()


# ==========================================================================================================================
# ==========================================================================================================================


def _warning_handler(message, category, filename, lineo, file=None, line=None) -> None:
    """Handles warnings for more compact vizualization. Mostly only because of blank signal convertion."""
    return

# ==========================================================================================================================


def main():
    warnings.showwarning = _warning_handler

    conn1, conn2 = multiprocessing.Pipe()

    app_gui = gui.App()

    app_interface = gui_interface.AppInterface(app_gui, conn1)

    proc = multiprocessing.Process(target=defs.run_backend, args=(conn2, ))
    proc.start()


    # blocking function
    app_interface.run()

    return

# ==========================================================================================================================

if __name__ == '__main__':
    main()
