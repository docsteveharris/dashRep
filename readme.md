## Summary

Example web app to demonstrate how we can use Plotly's Dash for Hylode

The majority of the work is in `./app`, and there's a separate 'app' for each webpage.

The principal sitrep app is found at `./app/app_sitrep.py`. The top half of the file contains a series of functions that are called (via the _callback_ decorators) by the layout specified in the second half of the file.

The `wrangle.py` module hold generic data wrangling functions.

And 'index.py' is the main coordinating module that in turn sets up the app ('app.py'), and routes to the different sub-apps (sitrep, debug etc.)

New apps and functionality can be deployed by duplicating and renaming `app_sitrep.py`, and then adding a new route in `index.py`.

## Installing

## Running

```sh
poetry shell
python app/index.py
```

It is often useful to run a JupyterLab instance during development.

```sh
poetry shell
jupyter lab --port 8899 --ip 0.0.0.0
```

Note
- the `--ip 0.0.0.0` flag allows me to connect to my dev machine across the network


## Sublime IDE notes
- enable LSP language server for pylsp globally; there's a problem with its per project isntallation