# Card Data Sync

Run server passing path to json file to sync to.
Post csv data to `/update`.

# Python

python version

## Usage

```sh
python main.py path/to/pack/set.json
```


# Go

go version (unused, don't use this)

## Usage

```sh
main path/to/pack/set.json
```

## Build

```sh
docker build -t gsheets-sync .
```

## Run

```sh
docker run --rm \
    -p 8080:8080 \
    -v /path/to/pack/json:/sync \
    gsheets-sync \
    /sync/set-name.json
```
