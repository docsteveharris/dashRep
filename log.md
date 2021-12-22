## 2021-12-21
Trying to dockerise the app
https://rants.tech/how-to-dockerise-a-python-application-properly/
Recommends using one of the lightweight python version (e.g. buster); alpine can be too light

Installing poetry so you can then install dependencies
https://github.com/python-poetry/poetry/discussions/3933

Nice example
Pin your poetry version and more
https://stackoverflow.com/a/54763270/992999

Found a simple dash hello world script for debugging
https://www.datacamp.com/community/tutorials/learn-build-dash-python
then
```sh
docker run -d -p 8050:8050 test
```
and navigate to localhost:8050 in the browser

Now do the same but use docker compose
https://www.technologyscout.net/2020/05/running-dash-in-docker/

2021-12-21t23:15:00
Successful deploy to UCLH
Had to hand load the little sqlite db
and load a local .env file
problems to fix with patient's who should have been discharged still appearing?



## 2021-12-22
Set-up functionality to clean sitrep data by checking census data

